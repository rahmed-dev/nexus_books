# Copyright (c) 2026, RAhmed-Dev and contributors
# For license information, please see license.txt

"""
API methods for Nexus Books PWA

Provides whitelisted endpoints for:
- Nexus Accounts (new) — list, create, update, set default
- Items — offline cache
- Transaction Categories — list with item field
- Parties — Customer/Supplier offline cache
- Transactions — list, get, amend, delete
- Summary statistics
"""

import json

import frappe
from frappe import _
from frappe.utils import flt


# ---------------------------------------------------------------------------
# Nexus Accounts
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_nexus_accounts():
	"""Get all active Nexus Accounts with current balance for PWA offline cache.

	Balance is always computed from nexus_books Financial Transactions.
	ERPNext GL is never queried for balance — linked_account is kept only
	for GL sync routing and reconciliation.

	Returns:
		list: Nexus Account records including balance and balance_source
	"""
	accounts = frappe.get_all(
		"Nexus Account",
		filters={"is_active": 1},
		fields=["name", "account_name", "account_type", "is_default", "is_active", "linked_account"],
		order_by="is_default desc, account_name asc",
	)

	if not accounts:
		return []

	nexus_balance_map = _compute_nexus_balances()

	for account in accounts:
		account["balance"] = flt(nexus_balance_map.get(account["name"], 0))
		account["balance_source"] = "nexus"
		# Keep linked_account in response — PWA needs it for reconcile account selector
		# (identifies which accounts have an ERPNext link)

	return accounts


def _compute_nexus_balances():
	"""Compute balance per Nexus Account from Financial Transaction in two bulk queries.

	Returns:
		dict: {nexus_account_name: balance}
	"""
	balance_map = {}

	# Query 1: amounts grouped by nexus_account (from-account side)
	from_account_rows = frappe.db.sql("""
		SELECT
			nexus_account,
			SUM(CASE WHEN transaction_type = 'Income'   THEN amount ELSE 0 END) AS income_total,
			SUM(CASE WHEN transaction_type = 'Expense'  THEN amount ELSE 0 END) AS expense_total,
			SUM(CASE WHEN transaction_type = 'Transfer' THEN amount ELSE 0 END) AS transfer_out_total
		FROM `tabFinancial Transaction`
		WHERE nexus_account IS NOT NULL
		  AND nexus_account != ''
		  AND docstatus = 1
		GROUP BY nexus_account
	""", as_dict=True)

	for row in from_account_rows:
		balance_map[row.nexus_account] = (
			flt(row.income_total) - flt(row.expense_total) - flt(row.transfer_out_total)
		)

	# Query 2: transfer amounts arriving into to_nexus_account
	to_account_rows = frappe.db.sql("""
		SELECT
			to_nexus_account,
			SUM(amount) AS transfer_in_total
		FROM `tabFinancial Transaction`
		WHERE to_nexus_account IS NOT NULL
		  AND to_nexus_account != ''
		  AND transaction_type = 'Transfer'
		  AND docstatus = 1
		GROUP BY to_nexus_account
	""", as_dict=True)

	for row in to_account_rows:
		balance_map[row.to_nexus_account] = (
			balance_map.get(row.to_nexus_account, 0) + flt(row.transfer_in_total)
		)

	return balance_map



@frappe.whitelist()
def create_nexus_account(account_name, account_type, is_default=0):
	"""Create a new Nexus Account from the PWA.

	Args:
		account_name (str): Friendly name, e.g. "Main Wallet"
		account_type (str): "Bank" or "Cash"
		is_default (int): 1 to mark as default account

	Returns:
		dict: Created Nexus Account fields
	"""
	if account_type not in ["Bank", "Cash"]:
		frappe.throw(_("Account type must be Bank or Cash"))

	if not account_name or not account_name.strip():
		frappe.throw(_("Account name is required"))

	doc = frappe.get_doc({
		"doctype": "Nexus Account",
		"account_name": account_name.strip(),
		"account_type": account_type,
		"is_active": 1,
		"is_default": frappe.utils.cint(is_default),
	})
	doc.insert(ignore_permissions=False)

	return _nexus_account_fields(doc)


@frappe.whitelist()
def update_nexus_account(name, account_name, account_type, is_default=0):
	"""Update a Nexus Account from the PWA.

	Args:
		name (str): Nexus Account docname
		account_name (str): Updated friendly name
		account_type (str): "Bank" or "Cash"
		is_default (int): 1 to mark as default account

	Returns:
		dict: Updated Nexus Account fields
	"""
	if account_type not in ["Bank", "Cash"]:
		frappe.throw(_("Account type must be Bank or Cash"))

	if not account_name or not account_name.strip():
		frappe.throw(_("Account name is required"))

	doc = frappe.get_doc("Nexus Account", name)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	doc.account_name = account_name.strip()
	doc.account_type = account_type
	doc.is_default = frappe.utils.cint(is_default)
	doc.save()  # NexusAccount.validate() clears other defaults if is_default=1

	return _nexus_account_fields(doc)


@frappe.whitelist()
def set_default_nexus_account(name):
	"""Mark a Nexus Account as the default (clears previous default).

	Args:
		name (str): Nexus Account docname

	Returns:
		dict: Updated Nexus Account fields
	"""
	doc = frappe.get_doc("Nexus Account", name)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	doc.is_default = 1
	doc.save()  # NexusAccount.validate() clears other defaults

	return _nexus_account_fields(doc)


def _nexus_account_fields(doc):
	"""Return PWA-safe fields from a Nexus Account document."""
	nexus_balance_map = _compute_nexus_balances()

	return {
		"name": doc.name,
		"account_name": doc.account_name,
		"account_type": doc.account_type,
		"is_default": doc.is_default,
		"is_active": doc.is_active,
		"balance": flt(nexus_balance_map.get(doc.name, 0)),
		"balance_source": "nexus",
		"linked_account": doc.linked_account,
	}


# ---------------------------------------------------------------------------
# Items (offline cache)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_items(limit=200):
	"""Get active non-stock service items for PWA offline cache.

	Args:
		limit (int): Max records to return

	Returns:
		list: Item records for offline selector
	"""
	return frappe.get_all(
		"Item",
		filters={"disabled": 0, "is_stock_item": 0},
		fields=["name", "item_name", "item_group"],
		order_by="item_name asc",
		limit=int(limit),
	)


# ---------------------------------------------------------------------------
# Transaction Categories
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_transaction_categories(category_type=None):
	"""Get active Transaction Categories for PWA offline cache.

	Args:
		category_type (str): Optional "Income", "Expense", or "Transfer"

	Returns:
		list: Categories including item field (determines if party is mandatory)
	"""
	filters = {"is_active": 1}
	if category_type:
		if category_type not in ["Income", "Expense", "Transfer"]:
			frappe.throw(_("Invalid category type"))
		filters["category_type"] = category_type

	return frappe.get_all(
		"Transaction Category",
		filters=filters,
		fields=[
			"name", "category_name", "category_code", "category_type",
			"is_active", "item", "gl_account", "color", "icon",
		],
		order_by="category_name asc",
	)


@frappe.whitelist()
def create_category(category_name, category_type, color=None, icon=None, gl_account=None):
	"""Create a new Transaction Category from the PWA.

	Args:
		category_name (str): Display name
		category_type (str): "Income", "Expense", or "Transfer"
		color (str): Hex color string
		icon (str): Lucide icon name
		gl_account (str): ERPNext GL account for Journal Entry posting (optional)

	Returns:
		dict: Created category fields
	"""
	if category_type not in ["Income", "Expense", "Transfer"]:
		frappe.throw(_("Invalid category type"))

	if not category_name or not category_name.strip():
		frappe.throw(_("Category name is required"))

	doc = frappe.get_doc({
		"doctype": "Transaction Category",
		"category_name": category_name.strip(),
		"category_type": category_type,
		"is_active": 1,
		"color": color or None,
		"icon": icon or None,
		"gl_account": gl_account or None,
	})
	doc.insert(ignore_permissions=False)

	return _category_fields(doc)


@frappe.whitelist()
def update_category(category, category_name, category_type, color=None, icon=None, gl_account=None):
	"""Update an existing Transaction Category from the PWA.

	Args:
		category (str): Docname to update
		category_name (str): New display name
		category_type (str): "Income", "Expense", or "Transfer"
		color (str): Hex color string
		icon (str): Lucide icon name
		gl_account (str): ERPNext GL account for Journal Entry posting (optional)

	Returns:
		dict: Updated category fields
	"""
	if category_type not in ["Income", "Expense", "Transfer"]:
		frappe.throw(_("Invalid category type"))

	if not category_name or not category_name.strip():
		frappe.throw(_("Category name is required"))

	doc = frappe.get_doc("Transaction Category", category)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	doc.category_name = category_name.strip()
	doc.category_type = category_type
	doc.color = color or None
	doc.icon = icon or None
	doc.gl_account = gl_account or None
	doc.save()

	return _category_fields(doc)


@frappe.whitelist()
def toggle_category_active(category):
	"""Toggle is_active on a Transaction Category.

	Args:
		category (str): Docname to toggle

	Returns:
		dict: Updated is_active value
	"""
	doc = frappe.get_doc("Transaction Category", category)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	doc.is_active = 0 if doc.is_active else 1
	doc.save()

	return {"name": doc.name, "is_active": doc.is_active}


def _category_fields(doc):
	"""Return PWA-safe fields from a Transaction Category document."""
	return {
		"name": doc.name,
		"category_name": doc.category_name,
		"category_type": doc.category_type,
		"is_active": doc.is_active,
		"item": doc.item,
		"gl_account": doc.gl_account,
		"color": doc.color,
		"icon": doc.icon,
	}


# ---------------------------------------------------------------------------
# Parties (Customer / Supplier offline cache)
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_cached_parties(party_type="Customer", limit=50):
	"""Get frequently used parties for PWA offline cache.

	Args:
		party_type (str): "Customer" or "Supplier"
		limit (int): Max records

	Returns:
		list: Party records sorted by usage frequency
	"""
	if party_type not in ["Customer", "Supplier"]:
		frappe.throw(_("Invalid party type. Must be Customer or Supplier."))

	if not limit:
		settings = frappe.get_single("Nexus Books Settings")
		limit = settings.cache_party_count or 50

	if party_type == "Customer":
		return frappe.db.sql("""
			SELECT
				c.name,
				c.customer_name AS party_name,
				c.mobile_no,
				c.email_id,
				c.image,
				COUNT(si.name) AS transaction_count
			FROM `tabCustomer` c
			LEFT JOIN `tabSales Invoice` si ON si.customer = c.name AND si.docstatus = 1
			WHERE c.disabled = 0
			GROUP BY c.name
			ORDER BY transaction_count DESC, c.modified DESC
			LIMIT %(limit)s
		""", {"limit": int(limit)}, as_dict=True)

	return frappe.db.sql("""
		SELECT
			s.name,
			s.supplier_name AS party_name,
			s.mobile_no,
			s.email_id,
			s.image,
			COUNT(pi.name) AS transaction_count
		FROM `tabSupplier` s
		LEFT JOIN `tabPurchase Invoice` pi ON pi.supplier = s.name AND pi.docstatus = 1
		WHERE s.disabled = 0
		GROUP BY s.name
		ORDER BY transaction_count DESC, s.modified DESC
		LIMIT %(limit)s
	""", {"limit": int(limit)}, as_dict=True)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_transactions(from_date=None, to_date=None, category=None, categories=None, limit=100):
	"""Get Financial Transactions with optional filters.

	Args:
		from_date (str): Start date inclusive (YYYY-MM-DD)
		to_date (str): End date inclusive (YYYY-MM-DD)
		category (str): Single category docname
		categories (str): JSON list of category docnames (multi-select)
		limit (int): Max records

	Returns:
		list: Transactions with category display fields and nexus account info
	"""
	filters = {"docstatus": ["<", 2]}

	if categories:
		category_list = frappe.parse_json(categories) if isinstance(categories, str) else categories
		if category_list:
			filters["category"] = ["in", category_list]
	elif category:
		filters["category"] = category

	if from_date and to_date:
		filters["date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["date"] = [">=", from_date]
	elif to_date:
		filters["date"] = ["<=", to_date]

	transactions = frappe.get_all(
		"Financial Transaction",
		filters=filters,
		fields=[
			"name", "transaction_type", "date", "category",
			"amount", "tax_amount", "customer", "supplier",
			"nexus_account", "to_nexus_account",
			"description", "gl_status", "gl_error",
		],
		order_by="date desc",
		limit=int(limit),
	)

	for txn in transactions:
		if txn.category:
			cat = frappe.get_cached_doc("Transaction Category", txn.category)
			txn["category_color"] = cat.color
			txn["category_icon"] = cat.icon
			txn["category_name"] = cat.category_name

	return transactions


@frappe.whitelist()
def get_transaction(name):
	"""Fetch a single Financial Transaction for edit pre-fill in the PWA.

	Args:
		name (str): Financial Transaction docname

	Returns:
		dict: Transaction fields for the edit form
	"""
	doc = frappe.get_doc("Financial Transaction", name)
	if not doc.has_permission("read"):
		frappe.throw(_("Insufficient permissions"))

	return {
		"name": doc.name,
		"transaction_type": doc.transaction_type,
		"amount": doc.amount,
		"tax_amount": doc.tax_amount,
		"date": str(doc.date) if doc.date else None,
		"category": doc.category,
		"customer": doc.customer,
		"supplier": doc.supplier,
		"nexus_account": doc.nexus_account,
		"to_nexus_account": doc.to_nexus_account,
		"description": doc.description,
		"gl_status": doc.gl_status,
		"docstatus": doc.docstatus,
	}


@frappe.whitelist()
def amend_transaction(name, data):
	"""Cancel and re-create a Financial Transaction with updated data.

	Args:
		name (str): Docname to amend
		data (dict|str): Updated field values

	Returns:
		dict: { name, docstatus } of the resulting document
	"""
	if isinstance(data, str):
		data = json.loads(data)

	original_doc = frappe.get_doc("Financial Transaction", name)
	if not original_doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	if original_doc.docstatus == 2:
		frappe.throw(_("Cannot edit a cancelled transaction"))

	editable_fields = [
		"transaction_type", "amount", "tax_amount", "date", "category",
		"customer", "supplier", "nexus_account", "to_nexus_account", "description",
	]

	if original_doc.docstatus == 1:
		original_doc.cancel()

		amended_doc = frappe.copy_doc(original_doc)
		amended_doc.amended_from = original_doc.name
		amended_doc.docstatus = 0
		amended_doc.gl_status = "pending"
		amended_doc.gl_error = None

		for field in editable_fields:
			if field in data:
				value = flt(data[field]) if field in ("amount", "tax_amount") else data[field]
				setattr(amended_doc, field, value)

		amended_doc.insert()
		amended_doc.submit()
		return {"name": amended_doc.name, "docstatus": amended_doc.docstatus}

	for field in editable_fields:
		if field in data:
			value = flt(data[field]) if field in ("amount", "tax_amount") else data[field]
			setattr(original_doc, field, value)

	original_doc.save()
	return {"name": original_doc.name, "docstatus": original_doc.docstatus}


@frappe.whitelist()
def cancel_and_delete_transaction(name):
	"""Cancel and permanently delete a Financial Transaction.

	Args:
		name (str): Docname to delete

	Returns:
		dict: { deleted: True }
	"""
	doc = frappe.get_doc("Financial Transaction", name)
	if not doc.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	if doc.docstatus == 1:
		doc.cancel()

	frappe.delete_doc("Financial Transaction", name, ignore_permissions=False, force=True)
	return {"deleted": True}


# ---------------------------------------------------------------------------
# Dashboard summary
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_transaction_summary(from_date=None, to_date=None):
	"""Get income/expense summary for dashboard.

	Args:
		from_date (str): Start date (defaults to current month start)
		to_date (str): End date (defaults to current month end)

	Returns:
		dict: { income, expense, balance, from_date, to_date }
	"""
	from frappe.utils import get_first_day, get_last_day, nowdate

	if not from_date:
		from_date = get_first_day(nowdate())
	if not to_date:
		to_date = get_last_day(nowdate())

	income = frappe.db.sql("""
		SELECT COALESCE(SUM(amount), 0) AS total
		FROM `tabFinancial Transaction`
		WHERE transaction_type = 'Income'
		  AND date BETWEEN %(from_date)s AND %(to_date)s
		  AND docstatus < 2
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)[0].total

	expense = frappe.db.sql("""
		SELECT COALESCE(SUM(amount), 0) AS total
		FROM `tabFinancial Transaction`
		WHERE transaction_type = 'Expense'
		  AND date BETWEEN %(from_date)s AND %(to_date)s
		  AND docstatus < 2
	""", {"from_date": from_date, "to_date": to_date}, as_dict=True)[0].total

	return {
		"income": income,
		"expense": expense,
		"balance": income - expense,
		"from_date": str(from_date),
		"to_date": str(to_date),
	}


@frappe.whitelist()
def get_recent_transactions(limit=20):
	"""Get recent transactions for dashboard (thin wrapper around get_transactions).

	Args:
		limit (int): Max records

	Returns:
		list: Recent transactions with category display fields
	"""
	return get_transactions(limit=limit)


@frappe.whitelist()
def get_default_currency():
	"""Get the default currency symbol for the PWA.

	Reads from Frappe System Settings.currency if available.
	Falls back to PKR (Rs.) if not configured or ERPNext is unavailable.

	Returns:
		dict: { currency: str, symbol: str }
	"""
	try:
		currency = frappe.db.get_single_value("System Settings", "currency")
		if currency:
			symbol = frappe.db.get_value("Currency", currency, "symbol") or currency
			return {"currency": currency, "symbol": symbol}
	except Exception:
		pass
	return {"currency": "PKR", "symbol": "Rs."}


@frappe.whitelist()
def get_monthly_totals(months=6):
	"""Get monthly income and expense totals for the bar chart.

	Returns data for the last N months, ordered oldest to newest.

	Args:
		months (int): Number of trailing months to include (default 6)

	Returns:
		dict: {
			labels: ['Jan 26', 'Feb 26', ...],
			income: [1200.0, 900.0, ...],
			expense: [800.0, 1100.0, ...]
		}
	"""
	import calendar
	from frappe.utils import add_months, get_first_day, nowdate

	months = frappe.utils.cint(months) or 6
	from_date = get_first_day(add_months(nowdate(), -(months - 1)))

	rows = frappe.db.sql("""
		SELECT
			YEAR(date)  AS txn_year,
			MONTH(date) AS txn_month,
			SUM(CASE WHEN transaction_type = 'Income'  THEN amount ELSE 0 END) AS income_total,
			SUM(CASE WHEN transaction_type = 'Expense' THEN amount ELSE 0 END) AS expense_total
		FROM `tabFinancial Transaction`
		WHERE docstatus < 2
		  AND date >= %(from_date)s
		GROUP BY YEAR(date), MONTH(date)
		ORDER BY txn_year ASC, txn_month ASC
	""", {"from_date": from_date}, as_dict=True)

	row_map = {(r.txn_year, r.txn_month): r for r in rows}

	labels = []
	income_totals = []
	expense_totals = []

	for month_offset in range(months):
		month_date = add_months(from_date, month_offset)
		year = frappe.utils.getdate(month_date).year
		month = frappe.utils.getdate(month_date).month
		label = f"{calendar.month_abbr[month]} {str(year)[2:]}"

		row = row_map.get((year, month), {})
		labels.append(label)
		income_totals.append(flt(row.get("income_total", 0)))
		expense_totals.append(flt(row.get("expense_total", 0)))

	return {"labels": labels, "income": income_totals, "expense": expense_totals}


# ---------------------------------------------------------------------------
# ERPNext Reconciliation
# ---------------------------------------------------------------------------

@frappe.whitelist()
def get_unmatched_erpnext_entries(from_date, to_date, nexus_account):
	"""Get ERPNext source documents not yet linked to a nexus_books transaction.

	Queries Journal Entries, Payment Entries, Sales Invoices, and Purchase Invoices
	in the given date range where nexus_books_ref is NULL (not created by nexus_books).

	Args:
		from_date (str): Start date inclusive (YYYY-MM-DD)
		to_date (str): End date inclusive (YYYY-MM-DD)
		nexus_account (str): Nexus Account docname

	Returns:
		list | dict: Unified list of unmatched entries, or {"error": "no_linked_account"}
	"""
	linked_account = frappe.db.get_value("Nexus Account", nexus_account, "linked_account")
	if not linked_account:
		return {"error": "no_linked_account"}

	try:
		import erpnext  # noqa: F401 — check ERPNext is installed
	except ImportError:
		return []

	entries = []

	# Journal Entries — any row with this account
	je_rows = frappe.db.sql("""
		SELECT
			je.name AS voucher_no,
			je.posting_date AS date,
			je.user_remark AS description,
			jea.debit_in_account_currency AS debit_amount,
			jea.credit_in_account_currency AS credit_amount
		FROM `tabJournal Entry` je
		JOIN `tabJournal Entry Account` jea ON jea.parent = je.name
		WHERE je.docstatus = 1
		  AND (je.nexus_books_ref IS NULL OR je.nexus_books_ref = '')
		  AND je.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND jea.account = %(linked_account)s
	""", {"from_date": from_date, "to_date": to_date, "linked_account": linked_account}, as_dict=True)

	for row in je_rows:
		# From the account's perspective: debit = money in, credit = money out
		amount = flt(row.debit_amount) or flt(row.credit_amount)
		debit_credit = "debit" if flt(row.debit_amount) > 0 else "credit"
		entries.append({
			"voucher_type": "Journal Entry",
			"voucher_no": row.voucher_no,
			"date": str(row.date),
			"amount": amount,
			"description": row.description or "",
			"debit_credit": debit_credit,
		})

	# Payment Entries — where this account is paid_from or paid_to
	pe_rows = frappe.db.sql("""
		SELECT
			pe.name AS voucher_no,
			pe.posting_date AS date,
			pe.remarks AS description,
			pe.paid_amount AS amount,
			CASE WHEN pe.paid_to = %(linked_account)s THEN 'debit' ELSE 'credit' END AS debit_credit
		FROM `tabPayment Entry` pe
		WHERE pe.docstatus = 1
		  AND (pe.nexus_books_ref IS NULL OR pe.nexus_books_ref = '')
		  AND pe.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND (pe.paid_from = %(linked_account)s OR pe.paid_to = %(linked_account)s)
	""", {"from_date": from_date, "to_date": to_date, "linked_account": linked_account}, as_dict=True)

	for row in pe_rows:
		entries.append({
			"voucher_type": "Payment Entry",
			"voucher_no": row.voucher_no,
			"date": str(row.date),
			"amount": flt(row.amount),
			"description": row.description or "",
			"debit_credit": row.debit_credit,
		})

	# Sales Invoices — debit_to = linked_account
	si_rows = frappe.db.sql("""
		SELECT
			si.name AS voucher_no,
			si.posting_date AS date,
			si.customer AS description,
			si.grand_total AS amount
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
		  AND (si.nexus_books_ref IS NULL OR si.nexus_books_ref = '')
		  AND si.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND si.debit_to = %(linked_account)s
	""", {"from_date": from_date, "to_date": to_date, "linked_account": linked_account}, as_dict=True)

	for row in si_rows:
		entries.append({
			"voucher_type": "Sales Invoice",
			"voucher_no": row.voucher_no,
			"date": str(row.date),
			"amount": flt(row.amount),
			"description": f"Sales Invoice — {row.description}",
			"debit_credit": "debit",
		})

	# Purchase Invoices — credit_to = linked_account
	pi_rows = frappe.db.sql("""
		SELECT
			pi.name AS voucher_no,
			pi.posting_date AS date,
			pi.supplier AS description,
			pi.grand_total AS amount
		FROM `tabPurchase Invoice` pi
		WHERE pi.docstatus = 1
		  AND (pi.nexus_books_ref IS NULL OR pi.nexus_books_ref = '')
		  AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
		  AND pi.credit_to = %(linked_account)s
	""", {"from_date": from_date, "to_date": to_date, "linked_account": linked_account}, as_dict=True)

	for row in pi_rows:
		entries.append({
			"voucher_type": "Purchase Invoice",
			"voucher_no": row.voucher_no,
			"date": str(row.date),
			"amount": flt(row.amount),
			"description": f"Purchase Invoice — {row.description}",
			"debit_credit": "credit",
		})

	# Sort all entries by date
	entries.sort(key=lambda entry: entry["date"])
	return entries


@frappe.whitelist()
def import_erpnext_entries(entries):
	"""Import ERPNext entries into nexus_books as Financial Transactions.

	Each entry must have: date, amount, nexus_account, transaction_type, voucher_no.
	Duplicate guard: skips entries whose voucher_no already exists as reference_name
	on a Financial Transaction.

	Args:
		entries (list|str): List of entry dicts from ReconcileSheet

	Returns:
		dict: { imported: N, skipped: N, errors: [...] }
	"""
	if isinstance(entries, str):
		entries = frappe.parse_json(entries)

	imported_count = 0
	skipped_count = 0
	import_errors = []

	for entry in entries:
		voucher_no = entry.get("voucher_no")
		if not voucher_no:
			skipped_count += 1
			continue

		# Duplicate guard — check if already imported
		already_imported = frappe.db.exists(
			"Financial Transaction",
			{"reference_name": voucher_no, "docstatus": ["<", 2]},
		)
		if already_imported:
			skipped_count += 1
			continue

		# Validate required fields
		missing_fields = [f for f in ("date", "amount", "nexus_account", "transaction_type") if not entry.get(f)]
		if missing_fields:
			import_errors.append(f"{voucher_no}: missing {', '.join(missing_fields)}")
			continue

		try:
			txn = frappe.get_doc({
				"doctype": "Financial Transaction",
				"transaction_type": entry["transaction_type"],
				"date": entry["date"],
				"amount": flt(entry["amount"]),
				"nexus_account": entry["nexus_account"],
				"category": entry.get("category") or None,
				"description": entry.get("description", ""),
				"erpnext_origin": 1,
				"reference_name": voucher_no,
			})
			txn.insert(ignore_permissions=True)
			txn.submit()
			frappe.db.commit()
			imported_count += 1
		except Exception as import_error:
			frappe.db.rollback()
			import_errors.append(f"{voucher_no}: {str(import_error)}")

	return {"imported": imported_count, "skipped": skipped_count, "errors": import_errors}


@frappe.whitelist()
def get_failed_gl_transactions(limit=50):
	"""Get Financial Transactions where ERPNext GL posting failed.

	Used by the Sync Errors sheet to display actionable failure reasons.

	Args:
		limit (int): Max records to return

	Returns:
		list: Failed transactions with error details
	"""
	return frappe.get_all(
		"Financial Transaction",
		filters={"gl_status": "failed", "docstatus": 1},
		fields=["name", "date", "amount", "transaction_type", "category", "gl_error"],
		order_by="date desc",
		limit=int(limit),
	)


@frappe.whitelist()
def retry_gl_sync(name):
	"""Reset gl_status to pending so the scheduler retries GL posting.

	Only allowed on transactions with gl_status = 'failed'.

	Args:
		name (str): Financial Transaction docname

	Returns:
		dict: { queued: True }
	"""
	txn = frappe.get_doc("Financial Transaction", name)
	if not txn.has_permission("write"):
		frappe.throw(_("Insufficient permissions"))

	if txn.gl_status != "failed":
		frappe.throw(_("Only failed transactions can be retried"))

	txn.db_set("gl_status", "pending")
	txn.db_set("gl_error", None)
	return {"queued": True}


@frappe.whitelist()
def get_category_breakdown(from_date, to_date, transaction_type):
	"""Get transaction totals grouped by category for donut charts.

	Args:
		from_date (str): Start date inclusive (YYYY-MM-DD)
		to_date (str): End date inclusive (YYYY-MM-DD)
		transaction_type (str): 'Income' or 'Expense'

	Returns:
		dict: {
			labels: ['Groceries', 'Transport', ...],
			amounts: [500.0, 200.0, ...],
			colors:  ['#e74c3c', '#3498db', ...]
		}
	"""
	if transaction_type not in ("Income", "Expense"):
		frappe.throw(_("transaction_type must be Income or Expense"))

	if not from_date or not to_date:
		frappe.throw(_("from_date and to_date are required"))

	rows = frappe.db.sql("""
		SELECT
			ft.category,
			tc.category_name,
			tc.color,
			SUM(ft.amount) AS total_amount
		FROM `tabFinancial Transaction` ft
		JOIN `tabTransaction Category` tc ON tc.name = ft.category
		WHERE ft.transaction_type = %(transaction_type)s
		  AND ft.date BETWEEN %(from_date)s AND %(to_date)s
		  AND ft.docstatus < 2
		  AND ft.category IS NOT NULL
		  AND ft.category != ''
		GROUP BY ft.category, tc.category_name, tc.color
		ORDER BY total_amount DESC
	""", {
		"transaction_type": transaction_type,
		"from_date": from_date,
		"to_date": to_date,
	}, as_dict=True)

	fallback_color = "#94a3b8"

	return {
		"labels":  [r.category_name for r in rows],
		"amounts": [flt(r.total_amount) for r in rows],
		"colors":  [r.color or fallback_color for r in rows],
	}
