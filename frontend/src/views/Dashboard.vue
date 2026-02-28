<template>
  <div
    class="flex flex-col pb-20"
    @touchstart.passive="onTouchStart"
    @touchmove.passive="onTouchMove"
    @touchend.passive="onTouchEnd"
  >
    <!-- Pull-to-refresh indicator -->
    <div
      v-if="isPullIndicatorVisible"
      class="flex items-center justify-center py-2 text-xs text-ink-gray-5"
    >
      {{ pullDistancePx >= PULL_THRESHOLD_PX ? 'Release to refresh' : 'Pull to refresh…' }}
    </div>

    <!-- Pending / failed IDB transactions -->
    <section v-if="pendingTransactions.length" class="mt-6">
      <p class="px-4 pb-1 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        Pending sync ({{ pendingTransactions.length }})
      </p>
      <TransactionCard
        v-for="txn in pendingTransactions"
        :key="`idb-${txn.id}`"
        :transaction="txn"
      />
    </section>

    <!-- Recent synced transactions from Frappe -->
    <section class="mt-6">
      <p class="px-4 pb-1 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        Recent
      </p>

      <div v-if="isLoading" class="py-10 text-center text-sm text-ink-gray-5">
        Loading…
      </div>

      <div
        v-else-if="!syncedTransactions.length && !pendingTransactions.length"
        class="py-10 text-center"
      >
        <p class="text-sm font-medium text-ink-gray-7">No transactions yet</p>
        <p class="mt-1 text-xs text-ink-gray-5">Tap + to add your first transaction</p>
      </div>

      <TransactionCard
        v-for="txn in syncedTransactions"
        :key="txn.name"
        :transaction="txn"
      />
    </section>

    <!-- FAB: opens AddTransactionForm -->
    <FAB @click="openAddForm" />

    <AddTransactionForm
      :is-open="showAddForm"
      @close="showAddForm = false"
      @saved="onTransactionSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useTransactionStore } from '@/stores/transactions'
import { useCategoryStore } from '@/stores/categories'
import TransactionCard from '@/components/TransactionCard.vue'
import FAB from '@/components/FAB.vue'
import AddTransactionForm from '@/components/AddTransactionForm.vue'

const transactionStore = useTransactionStore()
const categoryStore = useCategoryStore()

const syncedTransactions = ref([])
const isLoading = ref(false)
const showAddForm = ref(false)

// Pull-to-refresh state
const isPullIndicatorVisible = ref(false)
const pullDistancePx = ref(0)
const PULL_THRESHOLD_PX = 64
let touchStartY = 0

// IDB pending/syncing/failed transactions (shown separately with sync badges)
const pendingTransactions = computed(() =>
  transactionStore.transactions.filter(
    (txn) =>
      txn.sync_status === 'pending' ||
      txn.sync_status === 'syncing' ||
      txn.sync_status === 'failed',
  ),
)

function openAddForm() {
  showAddForm.value = true
}

async function onTransactionSaved() {
  await loadAll()
}

async function loadAll() {
  isLoading.value = true
  try {
    await Promise.all([
      transactionStore.loadRecentTransactions(),
      categoryStore.loadCategories(),
      loadTransactions(),
    ])
  } finally {
    isLoading.value = false
  }
}

async function loadTransactions() {
  try {
    const transactionsResponse = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_recent_transactions',
    })
    syncedTransactions.value = transactionsResponse ?? []
  } catch {
    // Offline — show IDB data only
  }
}

// --- Pull-to-refresh ---

function onTouchStart(event) {
  touchStartY = event.touches[0].clientY
  pullDistancePx.value = 0
}

function onTouchMove(event) {
  const scrolledToTop = window.scrollY === 0
  if (!scrolledToTop) return

  const dragDistance = event.touches[0].clientY - touchStartY
  if (dragDistance > 0) {
    pullDistancePx.value = dragDistance
    isPullIndicatorVisible.value = dragDistance > 16
  }
}

async function onTouchEnd() {
  if (pullDistancePx.value >= PULL_THRESHOLD_PX) {
    await loadAll()
  }
  isPullIndicatorVisible.value = false
  pullDistancePx.value = 0
}

onMounted(loadAll)
</script>
