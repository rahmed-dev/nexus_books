# Quick Spec: ERPNext Decoupling & Reconciliation

**Feature ID:** `erpnext-decoupling`
**Date:** 2026-03-06
**Status:** In Progress

---

## Goal

Make nexus_books fully functional without depending on ERPNext for core operations.
ERPNext becomes an optional background integration. Account balances and summaries are
always computed from nexus_books own Financial Transactions. A monthly reconciliation
flow lets the user pull accountant-added ERPNext entries back into nexus_books to keep
both systems in sync.

---

## Workflow This Supports

```
Month in progress  →  User records all transactions in nexus_books (offline-first)
End of month       →  Sync nexus_books → ERPNext (push, creates JE/PE/SI/PI)
Accountant step    →  Accountant adds missing entries directly in ERPNext
Reconciliation     →  User pulls unmatched ERPNext entries into nexus_books
Result             →  Both systems match → P&L is correct
```

---

## Components to Build

### 1. DocType Changes

**Financial Transaction** (existing)
- Add field: `erpnext_origin` — Check (default 0)
  - Marks transactions that were imported FROM ERPNext (not created in nexus_books)
  - Sync engine skips these — they must never be pushed back to ERPNext

**Custom Fields on ERPNext Documents** (via fixtures)
- `Journal Entry.nexus_books_ref` — Data, read-only, in section "Nexus Books"
- `Payment Entry.nexus_books_ref` — Data, read-only, in section "Nexus Books"
- `Sales Invoice.nexus_books_ref` — Data, read-only, in section "Nexus Books"
- `Purchase Invoice.nexus_books_ref` — Data, read-only, in section "Nexus Books"
- Purpose: set to Financial Transaction docname when nexus_books creates the ERPNext document
- Allows accountant to filter "not from nexus_books" in ERPNext Desk

---

### 2. Server Logic

#### `api.py` — Balance Calculation (change)
- `get_nexus_accounts()`: remove ERPNext GL balance priority entirely
- Always compute balance via `_compute_nexus_balances()`
- Remove `_get_erpnext_balance()` call from `get_nexus_accounts()` and `_nexus_account_fields()`
- `linked_account` field is kept on Nexus Account DocType — serves two critical purposes:
  1. **GL sync routing**: when the background scheduler posts a transaction to ERPNext, it reads `linked_account` from the transaction's `nexus_account` and `to_nexus_account` to know which ERPNext account to debit/credit
  2. **Reconciliation**: `get_unmatched_erpnext_entries` uses `linked_account` to query the correct ERPNext account for unmatched entries
- Balance display is the only thing removed from `linked_account` — all other uses remain

#### `api.py` — New: `get_unmatched_erpnext_entries(from_date, to_date, nexus_account)`
- Whitelisted. Gets the `linked_account` for the given Nexus Account.
- If no `linked_account` set: return `{"error": "no_linked_account"}`
- Queries 4 ERPNext document types for entries in date range where `nexus_books_ref` IS NULL:
  - `Journal Entry` — where any `Journal Entry Account` row has `account = linked_account`
  - `Payment Entry` — where `paid_from = linked_account` OR `paid_to = linked_account`
  - `Sales Invoice` — where `debit_to = linked_account`
  - `Purchase Invoice` — where `credit_to = linked_account`
- Returns unified list: `[{ date, amount, description, voucher_type, voucher_no, debit_credit }]`
- `debit_credit`: "debit" = money in, "credit" = money out (from the account's perspective)
- Gracefully returns empty list if ERPNext is not installed

#### `api.py` — New: `import_erpnext_entries(entries)`
- Whitelisted. Accepts list of entries (each with `date`, `amount`, `nexus_account`,
  `category`, `transaction_type`, `voucher_no`, `description`)
- Duplicate guard: skip any entry whose `voucher_no` already exists as `reference_name`
  on a Financial Transaction
- For each valid entry: creates and submits a Financial Transaction with
  `erpnext_origin = 1`, `gl_status = "erpnext_origin"`, `reference_name = voucher_no`
- Returns: `{ imported: N, skipped: N, errors: [...] }`

#### `sync_engine.py` — Set `nexus_books_ref` (change)
- When creating JE / PE / SI / PI in ERPNext, set `nexus_books_ref = txn.name`
  on the created document before saving

#### `hooks.py` — GL Posting Decoupled (change)
- Remove GL posting from `Financial Transaction.on_submit`
- Add scheduled job: `nexus_books.nexus_books.gl_scheduler.post_pending_gl_entries`
  - Frequency: every hour (or configurable via Nexus Books Settings)
  - Fetches all Financial Transactions with `gl_status = "pending"` and `docstatus = 1`
  - Attempts ERPNext GL posting for each
  - On success: sets `gl_status = "synced"`
  - On failure: sets `gl_status = "failed"`, logs error to `gl_error` field

#### `gl_scheduler.py` — New file
- `post_pending_gl_entries()`: the scheduled function
- Extracted from current `financial_transaction.py` on_submit GL logic

---

### 3. Client Logic

#### `api.py` — New: `get_failed_gl_transactions(limit=50)`
- Whitelisted. Returns Financial Transactions where `gl_status = "failed"` and `docstatus = 1`
- Fields returned: `name`, `date`, `amount`, `transaction_type`, `category`, `gl_error`
- Used by the Sync Errors sheet to display actionable failure reasons to the user

#### `api.py` — New: `retry_gl_sync(name)`
- Whitelisted. Resets `gl_status = "pending"` and clears `gl_error` on a single transaction
- Background scheduler picks it up on next run
- Returns `{ queued: true }`

#### `SettingsPage.vue` (change)
Under the **ERPNext Settings** section, add two buttons:

1. **"Pull from ERPNext"** button
   - Opens `ReconcileSheet.vue`
   - Purpose: import ERPNext transactions not yet in nexus_books (month-end reconciliation)
   - Disabled with tooltip "No accounts linked to ERPNext" if no Nexus Account has `linked_account` set

2. **"Sync Errors"** button
   - Opens `SyncErrorsSheet.vue`
   - Shows a count badge (red) with number of failed GL transactions
   - Badge count fetched on Settings page load via `get_failed_gl_transactions`
   - Badge hidden when count is 0

#### `SyncErrorsSheet.vue` — New component
- Uses `BottomSheet.vue`
- Title: "ERPNext Sync Errors"
- Lists all transactions with `gl_status = "failed"`
- Each row: date, amount, transaction type, category, **error message** (the `gl_error` value — plain language)
- Per-row action: "Retry" button → calls `retry_gl_sync(name)` → removes row from list on success
- "Retry All" button at the bottom
- Empty state: "No sync errors — all transactions posted to ERPNext"
- Error messages are shown as-is from `gl_error`; user can read them to understand what to fix
  (e.g., "Account 'Cash - TC' not found", "Missing mandatory field: cost_center")

#### `ReconcileSheet.vue` — New component
- Uses `BottomSheet.vue`
- **Step 1 — Select**: month picker (defaults to last month) + account selector (only accounts with `linked_account` set)
- **Step 2 — Review**: after "Fetch from ERPNext" — shows list of unmatched entries
  - Each row: date, description, amount (colour-coded debit/credit), category selector
  - Checkbox per row (all selected by default)
- **Step 3 — Import**: "Import Selected (N)" button → calls `import_erpnext_entries`
- Shows result: "3 imported, 1 skipped"
- Error state: "This account has no ERPNext account linked"
- Empty state: "All entries are already in nexus_books"

---

### 4. Dashboard Impact

This feature changes how account balances are computed. The following Dashboard components
are directly affected and must be verified after implementation:

#### `AccountBalanceCards.vue` (behaviour change — no code change required)
- Currently: balance may come from ERPNext GL (`balance_source: "erpnext"`) for linked accounts
- After: balance always comes from nexus_books Financial Transactions (`balance_source: "nexus"`)
- **Risk**: accounts that previously showed ERPNext GL balance will now show nexus-computed balance
  — these will differ until a full month-end sync + reconcile has been done
- **Expected outcome**: balances become accurate in real-time as transactions are added in nexus_books

#### `EquityCard.vue` (behaviour change — no code change required)
- Displays `totalBalance` = sum of all account balances from `stores/accounts.js`
- After balance source change, equity will reflect nexus_books data only
- No code change needed — it reads from the accounts store which already gets updated values

#### Dashboard Charts — Not Affected
- `BarChart` (monthly totals) → uses `get_monthly_totals` — queries Financial Transaction directly ✓
- `DonutChart` (category breakdown) → uses `get_category_breakdown` — queries Financial Transaction directly ✓
- Summary strip (income/expense/balance) → uses `get_transaction_summary` — queries Financial Transaction directly ✓
- None of these touch ERPNext GL — they are unaffected by this change

#### `AccountDetailView` — New (future consideration, out of scope for this feature)
- Tapping an account card on the Dashboard could show a filtered transaction list for that account
- Not in scope here — noted for Sprint 4 planning

---

### 5. Frontend Fix: Donut Chart Category Colors

#### Root Cause
`DonutChart.vue` has a bug where category colors from the database never appear in the chart.

frappe-charts `update()` only accepts new data — it does not support color changes after
chart creation. The current watcher calls `chartInstance.update(buildChartData())` when
colors change, but `buildChartData()` doesn't include colors, so frappe-charts keeps
whatever colors it was initialised with.

This happens because the chart is created once on `loading → false`, and subsequent
color changes (when API data arrives) trigger `update()` instead of a full recreation.

#### Fix — `DonutChart.vue`
- When props change and colors have changed since last render: **destroy and recreate the chart**
  instead of calling `update()`
- "Destroy" = clear `chartContainer.value.innerHTML` + set `chartInstance = null`
- frappe-charts has no official `destroy()` — innerHTML clear is the correct approach
- Track `lastColors` ref to detect when colors actually changed vs data-only change
- If only labels/amounts changed (colors unchanged): call `update()` as normal (no flicker)
- If colors changed: full recreate

#### `BarChart.vue` — Not Affected
- Colors are hardcoded `['#22c55e', '#f87171']` (income green, expense red)
- These are intentional fixed colours, not category-based
- No change needed

---

### 6. Bug Fix: Category Icon Missing on Synced Transactions

#### Root Cause
`TransactionCard.vue:116` — `resolvedCategory` computed returns `props.transaction` itself
for synced transactions (those with `category_name` set). The template then accesses
`resolvedCategory?.icon` — but synced transactions from `get_transactions` API have the
field named `category_icon`, not `icon`.

IDB transactions look up from the category store, which correctly has `icon`. So icons
appear for pending transactions but not for synced ones.

#### Fix — `TransactionCard.vue`
- In `resolvedCategory` computed: when returning a synced transaction, normalize field
  names to always expose `icon` and `color`:
  ```js
  if (props.transaction.category_name) {
    return {
      category_name: props.transaction.category_name,
      icon:  props.transaction.category_icon,   // normalize from category_icon → icon
      color: props.transaction.category_color,  // already correct
    }
  }
  ```
- No template change needed — `resolvedCategory?.icon` already works once normalized

---

### 7. UX Redesign: Add Transaction Flow

#### Current flow (clunky)
FAB → full scrollable form (bottom sheet) → user must manually tap category, amount, account

#### New flow (fast entry)
```
FAB tap
  → CategorySelector opens immediately (no intermediate form)
     → User taps a category
        → AmountEntrySheet opens (CategorySelector closes)
           → User types amount on custom numpad
           → Taps "Add Transaction" → saved
```

#### New component: `AmountEntrySheet.vue`
Uses `BottomSheet.vue`. Design uses existing Nexus Books component library — no custom
HTML/CSS beyond what's needed. Exact visual layout to be determined during implementation;
the spec defines behaviour and content, not pixel layout.

**Content (all must be visible without scrolling):**
- Transaction type switcher — `SegmentedControl.vue` (Expense / Income / Transfer)
- Selected category display — `CategoryAvatar.vue` + category name (tap to go back and change)
- Amount display — large text showing current entered amount with currency prefix
- Date — defaults to today, tap to change via native date input
- Account selector — horizontal scrollable row of `FilterChip.vue` chips, one per Nexus Account,
  default account pre-selected
- Custom numpad — digits 0–9, decimal point, backspace — built as a simple grid of buttons
  using existing Tailwind classes, no third-party numpad library
- "Add Transaction" primary button — full width, `Button` component

**Numpad behaviour:**
- Digits + decimal: build amount string character by character
- Backspace: remove last character
- Amount display updates live as user types

**Account chips:**
- Default account pre-selected on open
- Tapping a chip switches selected account

**"change category" / back:**
- Tapping the category display closes AmountEntrySheet and reopens CategorySelector
  so user can change category without losing transaction type

**Save:**
- Validates: amount > 0, account selected
- Saves via existing IDB → sync flow
- Closes on success, emits `saved`

#### Changes to `TransactionList.vue`
- `openAddForm()` renamed to `openCategorySelector()`
- On FAB tap: open CategorySelector, not AddTransactionForm
- On category selected: close CategorySelector, open AmountEntrySheet with selected category
- `AddTransactionForm` stays for **edit mode only** — full form with all fields

#### Advanced fields (description, tax, receipt)
- Not shown in the quick entry flow — kept in `AddTransactionForm` for edits
- Optional: a "More options" link below the numpad can open the full form (out of scope v1)

#### `AddTransactionForm.vue` — Edit mode only after this change
- No changes to the component itself
- Only opened from edit flow (`onEditTransaction`), not from FAB

---

## Behaviours

1. Account balance is always computed from nexus_books Financial Transactions — never from ERPNext GL
2. Transaction submit saves immediately to nexus_books; ERPNext GL posting runs on a background schedule
3. If ERPNext GL posting fails, the transaction is unaffected in nexus_books — `gl_status` stays `pending`, retried next schedule run
4. When nexus_books creates a JE/PE/SI/PI in ERPNext, it stamps `nexus_books_ref` on the document
5. Accountant can filter ERPNext documents by `nexus_books_ref is not set` to see only manually-added entries
6. Reconcile button in Settings opens a bottom sheet — pick month + account, fetch, review, import
7. Imported entries have `erpnext_origin = 1` — sync engine skips them permanently
8. When ERPNext GL posting fails, `gl_error` is stored on the transaction with the raw error message
9. Settings page shows a "Sync Errors" badge with the count of failed transactions
10. User can open Sync Errors sheet, read the reason, fix the underlying configuration, and retry

---

## Validations

1. `import_erpnext_entries`: each entry must have `date`, `amount`, `nexus_account`, `transaction_type`
2. `get_unmatched_erpnext_entries`: if Nexus Account has no `linked_account`, return `error: no_linked_account`
3. Duplicate guard: check `reference_name` against existing Financial Transactions before importing
4. Sync engine: skip Financial Transactions where `erpnext_origin = 1`
5. `retry_gl_sync`: only allowed on transactions with `gl_status = "failed"` — throws if called on other statuses

---

## Permissions

- All nexus_books API methods: standard Frappe user permissions
- ERPNext document queries: read-only, uses existing session permissions
- Import creates Financial Transactions: requires write permission on Financial Transaction

---

## Edge Cases

- ERPNext not installed → `get_unmatched_erpnext_entries` returns `[]` gracefully; Reconcile button shows "ERPNext not available"
- Account has no `linked_account` → clear message in bottom sheet, no crash
- Partial import (some entries fail) → successful entries imported, failed ones shown with inline error
- GL scheduler runs while a transaction is mid-sync → idempotent check on `gl_status` prevents double-posting

---

## Out of Scope

- Real-time two-way sync
- Automatic conflict resolution
- Pulling from ERPNext reports or analytics (GL entries of source documents only)
- Removing `linked_account` from Nexus Account (kept for ERPNext sync routing)
- Auto-categorising imported entries (user assigns category manually in review step)
