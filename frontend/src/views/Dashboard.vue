<template>
  <div class="flex flex-col gap-5 px-4 pb-24 pt-4">

    <DashboardHeader />

    <template v-for="widgetId in dashboardStore.orderedEnabledWidgetIds" :key="widgetId">

      <!-- Monthly Summary -->
      <section v-if="widgetId === 'summary-strip'">
        <p class="mb-2 text-xs font-medium uppercase tracking-wide text-ink-gray-4">
          {{ currentMonthLabel }}
        </p>
        <SummaryStrip
          :balance="summary.income - summary.expense"
          :income="summary.income"
          :expense="summary.expense"
          :currency-symbol="settingsStore.currencySymbol"
          :loading="loadingSummary"
        />
      </section>

      <!-- Account Balance Cards -->
      <AccountBalanceCards
        v-else-if="widgetId === 'account-cards'"
        :accounts="accountStore.accounts"
        :currency-symbol="settingsStore.currencySymbol"
        :loading="accountStore.isLoading"
      />

      <!-- Equity Card -->
      <EquityCard
        v-else-if="widgetId === 'equity-card'"
        :equity="accountStore.totalBalance"
        :currency-symbol="settingsStore.currencySymbol"
        :loading="accountStore.isLoading"
      />

      <!-- Bar Chart -->
      <BarChart
        v-else-if="widgetId === 'bar-chart'"
        :labels="monthlyTotals.labels"
        :income="monthlyTotals.income"
        :expense="monthlyTotals.expense"
        :loading="loadingMonthly"
      />

      <!-- Donut Chart Tabs -->
      <DonutChartTabs
        v-else-if="widgetId === 'donut-chart'"
        :expense-labels="expenseBreakdown.labels"
        :expense-amounts="expenseBreakdown.amounts"
        :expense-colors="expenseBreakdown.colors"
        :income-labels="incomeBreakdown.labels"
        :income-amounts="incomeBreakdown.amounts"
        :income-colors="incomeBreakdown.colors"
        :loading="loadingBreakdown"
      />

    </template>

    <FAB @click="openCategorySelector" />

    <CategorySelector
      v-if="showCategorySelector"
      @select="onCategorySelected"
      @close="showCategorySelector = false"
    />

    <AmountEntrySheet
      v-if="showAmountEntry"
      :selected-category="pendingCategory"
      :initial-type="pendingCategory?.category_type ?? 'Expense'"
      @saved="onTransactionSaved"
      @close="showAmountEntry = false"
      @change-category="onChangeCategoryFromAmount"
    />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useAccountStore } from '@/stores/accounts'
import { useSettingsStore } from '@/stores/settings'
import { useDashboardStore } from '@/stores/dashboard'
import SummaryStrip from '@/components/SummaryStrip.vue'
import AccountBalanceCards from '@/components/AccountBalanceCards.vue'
import EquityCard from '@/components/EquityCard.vue'
import BarChart from '@/components/BarChart.vue'
import DonutChartTabs from '@/components/DonutChartTabs.vue'
import FAB from '@/components/FAB.vue'
import CategorySelector from '@/components/CategorySelector.vue'
import AmountEntrySheet from '@/components/AmountEntrySheet.vue'
import DashboardHeader from '@/components/DashboardHeader.vue'

const accountStore = useAccountStore()
const settingsStore = useSettingsStore()
const dashboardStore = useDashboardStore()

const showCategorySelector = ref(false)
const showAmountEntry = ref(false)
const pendingCategory = ref(null)

function openCategorySelector() {
  pendingCategory.value = null
  showCategorySelector.value = true
}

function onCategorySelected(category) {
  pendingCategory.value = category
  showCategorySelector.value = false
  showAmountEntry.value = true
}

function onChangeCategoryFromAmount() {
  showAmountEntry.value = false
  showCategorySelector.value = true
}

dashboardStore.loadConfig()

function getMonthRange() {
  const now = new Date()
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1)
  const lastDay  = new Date(now.getFullYear(), now.getMonth() + 1, 0)
  const toISO = (d) => d.toISOString().split('T')[0]
  return { from_date: toISO(firstDay), to_date: toISO(lastDay) }
}

const currentMonthLabel = computed(() =>
  new Date().toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
)

const loadingSummary = ref(true)
const summary = reactive({ income: 0, expense: 0 })

async function fetchSummary() {
  const { from_date, to_date } = getMonthRange()
  const result = await frappeRequest({
    url: '/api/method/nexus_books.nexus_books.api.get_transaction_summary',
    params: { from_date, to_date },
  })
  summary.income  = result?.income  || 0
  summary.expense = result?.expense || 0
}

const loadingMonthly = ref(true)
const monthlyTotals = reactive({ labels: [], income: [], expense: [] })

async function fetchMonthlyTotals() {
  const result = await frappeRequest({
    url: '/api/method/nexus_books.nexus_books.api.get_monthly_totals',
    params: { months: 6 },
  })
  monthlyTotals.labels  = result?.labels  || []
  monthlyTotals.income  = result?.income  || []
  monthlyTotals.expense = result?.expense || []
}

const loadingBreakdown = ref(true)
const expenseBreakdown = reactive({ labels: [], amounts: [], colors: [] })
const incomeBreakdown  = reactive({ labels: [], amounts: [], colors: [] })

async function fetchCategoryBreakdown() {
  const { from_date, to_date } = getMonthRange()
  const [expenseResult, incomeResult] = await Promise.all([
    frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_category_breakdown',
      params: { from_date, to_date, transaction_type: 'Expense' },
    }),
    frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_category_breakdown',
      params: { from_date, to_date, transaction_type: 'Income' },
    }),
  ])
  expenseBreakdown.labels  = expenseResult?.labels  || []
  expenseBreakdown.amounts = expenseResult?.amounts || []
  expenseBreakdown.colors  = expenseResult?.colors  || []
  incomeBreakdown.labels  = incomeResult?.labels  || []
  incomeBreakdown.amounts = incomeResult?.amounts || []
  incomeBreakdown.colors  = incomeResult?.colors  || []
}

onMounted(async () => {
  await Promise.allSettled([
    fetchSummary().finally(() => { loadingSummary.value = false }),
    fetchMonthlyTotals().finally(() => { loadingMonthly.value = false }),
    fetchCategoryBreakdown().finally(() => { loadingBreakdown.value = false }),
  ])
})

async function onTransactionSaved() {
  showTransactionForm.value = false
  loadingSummary.value   = true
  loadingMonthly.value   = true
  loadingBreakdown.value = true
  await Promise.allSettled([
    fetchSummary().finally(() => { loadingSummary.value = false }),
    fetchMonthlyTotals().finally(() => { loadingMonthly.value = false }),
    fetchCategoryBreakdown().finally(() => { loadingBreakdown.value = false }),
  ])
}
</script>
