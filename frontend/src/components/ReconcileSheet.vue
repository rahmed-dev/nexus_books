<template>
  <BottomSheet title="Pull from ERPNext" @close="emit('close')">

    <!-- Step 1: Select month + account -->
    <div v-if="step === 'select'" class="px-4 pb-4 space-y-4">

      <div v-if="linkedAccounts.length === 0" class="py-8 text-center text-sm text-ink-gray-5">
        No accounts linked to ERPNext. Link an account in Nexus Books Settings to use reconciliation.
      </div>

      <template v-else>
        <!-- Month picker -->
        <FormField label="Month">
          <input
            v-model="selectedMonth"
            type="month"
            class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          />
        </FormField>

        <!-- Account selector -->
        <FormField label="Account">
          <select
            v-model="selectedAccountName"
            class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          >
            <option v-for="account in linkedAccounts" :key="account.name" :value="account.name">
              {{ account.account_name }}
            </option>
          </select>
        </FormField>

        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white active:bg-surface-gray-6 disabled:opacity-50"
          :disabled="!selectedAccountName || isFetching"
          @click="fetchEntries"
        >
          {{ isFetching ? 'Fetching…' : 'Fetch from ERPNext' }}
        </button>

        <p v-if="fetchError" class="text-center text-xs text-red-500">{{ fetchError }}</p>
      </template>

    </div>

    <!-- Step 2: Review entries -->
    <div v-else-if="step === 'review'">

      <!-- Empty state -->
      <div v-if="!unmatchedEntries.length" class="px-4 py-10 text-center text-sm text-ink-gray-5">
        All entries are already in nexus_books. Nothing to import.
      </div>

      <!-- Entry list -->
      <div v-else class="divide-y divide-outline-gray-1">
        <div
          v-for="(entry, index) in unmatchedEntries"
          :key="entry.voucher_no"
          class="px-4 py-3"
        >
          <div class="flex items-center gap-3 mb-2">
            <!-- Row select checkbox -->
            <input
              v-model="entry.selected"
              type="checkbox"
              class="h-4 w-4 rounded accent-ink-gray-9"
            />
            <div class="min-w-0 flex-1">
              <div class="flex items-baseline justify-between gap-2">
                <p class="truncate text-sm font-medium text-ink-gray-9">{{ entry.description || entry.voucher_type }}</p>
                <span
                  class="shrink-0 text-sm font-semibold"
                  :class="entry.debit_credit === 'debit' ? 'text-green-600' : 'text-ink-gray-9'"
                >
                  {{ entry.debit_credit === 'debit' ? '+' : '-' }}{{ formatAmount(entry.amount) }}
                </span>
              </div>
              <p class="text-xs text-ink-gray-5">{{ formatDate(entry.date) }} · {{ entry.voucher_no }}</p>
            </div>
          </div>

          <!-- Category + type selectors for this row -->
          <div class="ml-7 flex gap-2">
            <select
              v-model="entry.transaction_type"
              class="flex-1 rounded-lg border border-outline-gray-2 bg-surface-gray-1 px-2 py-1.5 text-xs text-ink-gray-9 focus:outline-none"
            >
              <option value="Income">Income</option>
              <option value="Expense">Expense</option>
              <option value="Transfer">Transfer</option>
            </select>
            <select
              v-model="entry.category"
              class="flex-1 rounded-lg border border-outline-gray-2 bg-surface-gray-1 px-2 py-1.5 text-xs text-ink-gray-9 focus:outline-none"
            >
              <option value="">No category</option>
              <option
                v-for="cat in filteredCategories(entry.transaction_type)"
                :key="cat.name"
                :value="cat.name"
              >
                {{ cat.category_name }}
              </option>
            </select>
          </div>
        </div>
      </div>

    </div>

    <!-- Step 3: Result -->
    <div v-else-if="step === 'result'" class="px-4 py-8 text-center space-y-2">
      <p class="text-sm font-medium text-ink-gray-9">Import complete</p>
      <p class="text-sm text-ink-gray-6">{{ importResult.imported }} imported · {{ importResult.skipped }} skipped</p>
      <ul v-if="importResult.errors.length" class="mt-3 space-y-1 text-left">
        <li v-for="err in importResult.errors" :key="err" class="text-xs text-red-500">{{ err }}</li>
      </ul>
    </div>

    <!-- Footer buttons -->
    <template #footer>
      <!-- Review step: back + import -->
      <div v-if="step === 'review' && unmatchedEntries.length" class="flex gap-3 px-4 py-3">
        <button
          type="button"
          class="rounded-xl border border-outline-gray-2 px-4 py-3 text-sm font-medium text-ink-gray-7 active:bg-surface-gray-1"
          @click="step = 'select'"
        >
          Back
        </button>
        <button
          type="button"
          class="flex-1 rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white active:bg-surface-gray-6 disabled:opacity-50"
          :disabled="!selectedCount || isImporting"
          @click="importSelected"
        >
          {{ isImporting ? 'Importing…' : `Import Selected (${selectedCount})` }}
        </button>
      </div>

      <!-- Result step: done -->
      <div v-else-if="step === 'result'" class="px-4 py-3">
        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white active:bg-surface-gray-6"
          @click="emit('close')"
        >
          Done
        </button>
      </div>
    </template>

  </BottomSheet>
</template>

<script setup>
import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useAccountStore } from '@/stores/accounts'
import { useCategoryStore } from '@/stores/categories'
import BottomSheet from '@/components/BottomSheet.vue'
import FormField from '@/components/FormField.vue'

const emit = defineEmits(['close'])

const accountStore = useAccountStore()
const categoryStore = useCategoryStore()

const step = ref('select')
const isFetching = ref(false)
const isImporting = ref(false)
const fetchError = ref(null)
const unmatchedEntries = ref([])
const importResult = ref({ imported: 0, skipped: 0, errors: [] })

// Default to last month
const lastMonth = (() => {
  const d = new Date()
  d.setMonth(d.getMonth() - 1)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
})()
const selectedMonth = ref(lastMonth)
const selectedAccountName = ref('')

const linkedAccounts = computed(() =>
  accountStore.accounts.filter((a) => a.linked_account),
)

const selectedCount = computed(() =>
  unmatchedEntries.value.filter((e) => e.selected).length,
)

// Set first linked account as default when list loads
if (linkedAccounts.value.length) {
  selectedAccountName.value = linkedAccounts.value[0].name
}

function filteredCategories(transactionType) {
  if (!transactionType || transactionType === 'Transfer') {
    return categoryStore.activeCategories
  }
  return categoryStore.categories.filter(
    (c) => c.category_type === transactionType && c.is_active,
  )
}

async function fetchEntries() {
  fetchError.value = null
  isFetching.value = true
  try {
    // Build from/to dates from selected month (YYYY-MM)
    const [year, month] = selectedMonth.value.split('-')
    const fromDate = `${year}-${month}-01`
    const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate()
    const toDate = `${year}-${month}-${String(lastDay).padStart(2, '0')}`

    const result = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_unmatched_erpnext_entries',
      params: { from_date: fromDate, to_date: toDate, nexus_account: selectedAccountName.value },
    })

    if (result && result.error === 'no_linked_account') {
      fetchError.value = 'This account has no ERPNext account linked.'
      return
    }

    // Enrich entries with mutable UI state
    unmatchedEntries.value = (result || []).map((entry) => ({
      ...entry,
      selected: true,
      nexus_account: selectedAccountName.value,
      transaction_type: entry.debit_credit === 'debit' ? 'Income' : 'Expense',
      category: '',
    }))
    step.value = 'review'
  } catch {
    fetchError.value = 'Failed to fetch from ERPNext. Check your connection.'
  } finally {
    isFetching.value = false
  }
}

async function importSelected() {
  isImporting.value = true
  try {
    const entriesToImport = unmatchedEntries.value
      .filter((e) => e.selected)
      .map((e) => ({
        date: e.date,
        amount: e.amount,
        nexus_account: e.nexus_account,
        transaction_type: e.transaction_type,
        category: e.category || null,
        voucher_no: e.voucher_no,
        description: e.description,
      }))

    const result = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.import_erpnext_entries',
      params: { entries: JSON.stringify(entriesToImport) },
    })

    importResult.value = result || { imported: 0, skipped: 0, errors: [] }
    step.value = 'result'
  } catch {
    fetchError.value = 'Import failed. Please try again.'
  } finally {
    isImporting.value = false
  }
}

function formatAmount(amount) {
  return Number(amount || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}
</script>
