<template>
  <div class="flex flex-col pb-20">

    <!-- Filter bar -->
    <div class="sticky top-0 z-10 bg-surface-white px-4 py-3 shadow-sm">
      <button
        type="button"
        class="flex w-full items-center justify-between rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-2.5 active:bg-surface-gray-2"
        @click="showFilterSheet = true"
      >
        <span class="text-sm text-ink-gray-6">{{ filterSummaryLabel }}</span>
        <div class="relative ml-2 shrink-0">
          <!-- Sliders / filter icon -->
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 6a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <!-- Active indicator dot -->
          <span
            v-if="isFilterActive"
            class="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-surface-gray-7"
          />
        </div>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="py-10 text-center text-sm text-ink-gray-5">
      Loading…
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else-if="!allTransactions.length"
      title="No transactions found"
      subtitle="Try a different filter or add a transaction"
    />

    <!-- Transaction list -->
    <section v-else class="mt-2">
      <TransactionCard
        v-for="txn in allTransactions"
        :key="txn.name ?? String(txn.id)"
        :transaction="txn"
        @edit="onEditTransaction"
        @delete-request="onDeleteRequest"
      />
    </section>

    <FAB @click="openCategorySelector" />

    <TransactionFilterSheet
      :is-open="showFilterSheet"
      :categories="categoryStore.categories"
      :filter="activeFilter"
      @close="showFilterSheet = false"
      @apply="onFilterApply"
    />

    <!-- Category selector — FAB add flow -->
    <CategorySelector
      v-if="showCategorySelector"
      :selected-category-id="pendingCategory?.name ?? null"
      @select="onCategorySelectedForAdd"
      @close="showCategorySelector = false"
    />

    <!-- Amount entry — fast add flow (after category selected) -->
    <AmountEntrySheet
      v-if="showAmountEntry"
      :selected-category="pendingCategory"
      :initial-type="pendingCategory?.category_type ?? 'Expense'"
      @saved="onTransactionSaved"
      @close="showAmountEntry = false"
      @change-category="onChangeCategoryFromAmount"
    />

    <!-- Edit form — only for editing existing transactions -->
    <AddTransactionForm
      :is-open="showTransactionForm"
      :transaction="editingTransaction"
      @close="onTransactionFormClosed"
      @saved="onTransactionSaved"
    />

    <ConfirmDeleteSheet
      :is-open="showDeleteConfirm"
      :transaction="deletingTransaction"
      :is-deleting="isDeleting"
      @close="showDeleteConfirm = false"
      @confirm="onDeleteConfirmed"
    />

    <!-- Edit load error toast -->
    <Transition name="fade">
      <div
        v-if="editLoadError"
        class="fixed bottom-24 inset-x-4 z-40 rounded-xl bg-surface-gray-7 px-4 py-3 text-center text-sm text-white shadow-lg"
      >
        {{ editLoadError }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useCategoryStore } from '@/stores/categories'
import { useTransactionStore } from '@/stores/transactions'
import TransactionCard from '@/components/TransactionCard.vue'
import FAB from '@/components/FAB.vue'
import AddTransactionForm from '@/components/AddTransactionForm.vue'
import AmountEntrySheet from '@/components/AmountEntrySheet.vue'
import CategorySelector from '@/components/CategorySelector.vue'
import ConfirmDeleteSheet from '@/components/ConfirmDeleteSheet.vue'
import TransactionFilterSheet from '@/components/TransactionFilterSheet.vue'
import EmptyState from '@/components/EmptyState.vue'

const categoryStore = useCategoryStore()
const transactionStore = useTransactionStore()

const syncedTransactions = ref([])
const idbUnsyncedTransactions = ref([])
const isLoading = ref(false)

// IDB pending/failed transactions displayed above synced ones so the user
// always sees a newly added transaction even when sync hasn't completed yet.
const allTransactions = computed(() => [...idbUnsyncedTransactions.value, ...syncedTransactions.value])
const showFilterSheet = ref(false)

const showCategorySelector = ref(false)
const showAmountEntry = ref(false)
const pendingCategory = ref(null)

const showTransactionForm = ref(false)
const editingTransaction = ref(null)
const showDeleteConfirm = ref(false)
const deletingTransaction = ref(null)
const isDeleting = ref(false)
const editLoadError = ref(null)

const PERIOD_OPTIONS = [
  { value: 'month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'year', label: 'This Year' },
  { value: 'all', label: 'All' },
  { value: 'custom', label: 'Custom' },
]

const activeFilter = ref({
  period: 'all',
  fromDate: '',
  toDate: '',
  selectedCategories: [],
})

// --- Filter summary label shown on the bar button ---

const filterSummaryLabel = computed(() => {
  const periodOption = PERIOD_OPTIONS.find((o) => o.value === activeFilter.value.period)
  let periodText = periodOption?.label ?? 'Custom'
  if (activeFilter.value.period === 'custom') {
    periodText =
      activeFilter.value.fromDate && activeFilter.value.toDate
        ? `${activeFilter.value.fromDate} – ${activeFilter.value.toDate}`
        : 'Custom range'
  }

  const catCount = activeFilter.value.selectedCategories.length
  let catText
  if (catCount === 0) {
    catText = 'All categories'
  } else if (catCount === 1) {
    const match = categoryStore.categories.find(
      (c) => c.name === activeFilter.value.selectedCategories[0],
    )
    catText = match?.category_name ?? '1 category'
  } else {
    catText = `${catCount} categories`
  }

  return `${periodText} · ${catText}`
})

// Dot shows when filter differs from default (This Month, all categories)
const isFilterActive = computed(
  () => activeFilter.value.period !== 'month' || activeFilter.value.selectedCategories.length > 0,
)

// --- Date range helpers ---

function getDateRange(filter) {
  const today = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const fmt = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`

  if (filter.period === 'custom') {
    return { from_date: filter.fromDate || null, to_date: filter.toDate || null }
  }
  if (filter.period === 'month') {
    return { from_date: fmt(new Date(today.getFullYear(), today.getMonth(), 1)), to_date: fmt(today) }
  }
  if (filter.period === 'last_month') {
    return {
      from_date: fmt(new Date(today.getFullYear(), today.getMonth() - 1, 1)),
      to_date: fmt(new Date(today.getFullYear(), today.getMonth(), 0)),
    }
  }
  if (filter.period === 'year') {
    return { from_date: fmt(new Date(today.getFullYear(), 0, 1)), to_date: fmt(today) }
  }
  return { from_date: null, to_date: null }
}

// --- Load transactions ---

async function loadIdbUnsyncedTransactions() {
  idbUnsyncedTransactions.value = await transactionStore.getUnsyncedTransactions()
}

async function loadSyncedTransactions() {
  isLoading.value = true
  try {
    const { from_date, to_date } = getDateRange(activeFilter.value)
    const params = { limit: 200 }
    if (from_date) params.from_date = from_date
    if (to_date) params.to_date = to_date
    if (activeFilter.value.selectedCategories.length) {
      params.categories = JSON.stringify(activeFilter.value.selectedCategories)
    }

    syncedTransactions.value =
      (await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.get_transactions',
        params,
      })) ?? []
  } catch {
    // Offline — list stays empty
  } finally {
    isLoading.value = false
  }
}

function onFilterApply(newFilter) {
  activeFilter.value = newFilter
  showFilterSheet.value = false
}

watch(activeFilter, loadSyncedTransactions, { deep: true })

// --- Add / Edit / Delete ---

function openCategorySelector() {
  pendingCategory.value = null
  showCategorySelector.value = true
}

function onCategorySelectedForAdd(category) {
  pendingCategory.value = category
  showCategorySelector.value = false
  showAmountEntry.value = true
}

function onChangeCategoryFromAmount() {
  // User tapped "change category" in AmountEntrySheet — go back to CategorySelector
  showAmountEntry.value = false
  showCategorySelector.value = true
}

function onTransactionFormClosed() {
  showTransactionForm.value = false
  editingTransaction.value = null
}

async function onTransactionSaved() {
  await Promise.all([loadIdbUnsyncedTransactions(), loadSyncedTransactions()])
  // Reload again after 2 s — by then sync may have completed, moving the
  // transaction from IDB-pending into the Frappe-synced list.
  setTimeout(
    () => Promise.all([loadIdbUnsyncedTransactions(), loadSyncedTransactions()]),
    2000,
  )
}

async function onEditTransaction(transaction) {
  if (transaction.name) {
    try {
      const fullTransaction = await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.get_transaction',
        params: { name: transaction.name },
      })
      editingTransaction.value = {
        name: fullTransaction.name,
        docstatus: fullTransaction.docstatus,
        transaction_type: fullTransaction.transaction_type,
        amount: fullTransaction.amount,
        date: fullTransaction.date,
        category_id: fullTransaction.category,
        category_label: transaction.category_name || fullTransaction.category,
        customer_id: fullTransaction.customer,
        supplier_id: fullTransaction.supplier,
        description: fullTransaction.description,
        tax_amount: fullTransaction.tax_amount,
        payment_account_id: fullTransaction.payment_account,
      }
    } catch {
      editLoadError.value = 'Could not load transaction. Please try again.'
      setTimeout(() => {
        editLoadError.value = null
      }, 3000)
      return
    }
  } else {
    editingTransaction.value = transaction
  }
  showTransactionForm.value = true
}

function onDeleteRequest(transaction) {
  deletingTransaction.value = transaction
  showDeleteConfirm.value = true
}

async function onDeleteConfirmed() {
  const transaction = deletingTransaction.value
  isDeleting.value = true
  try {
    if (transaction.name) {
      await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.cancel_and_delete_transaction',
        params: { name: transaction.name },
      })
      await loadSyncedTransactions()
    }
    showDeleteConfirm.value = false
    deletingTransaction.value = null
  } catch {
    // Keep sheet open so user sees something failed
  } finally {
    isDeleting.value = false
  }
}

onMounted(async () => {
  await Promise.all([categoryStore.loadCategories(), loadIdbUnsyncedTransactions(), loadSyncedTransactions()])
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
