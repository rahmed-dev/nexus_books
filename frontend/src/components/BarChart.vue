<template>
  <div>
    <!-- Loading skeleton (shown while fetching) -->
    <div v-show="loading" class="flex h-44 items-end gap-1 px-2">
      <div
        v-for="n in 6"
        :key="n"
        class="flex-1 animate-pulse rounded-t bg-surface-gray-3"
        :style="{ height: `${30 + (n * 13) % 60}%` }"
      ></div>
    </div>

    <!-- Empty state (shown when loaded but no data) -->
    <EmptyState
      v-show="!loading && isEmpty"
      title="No transactions yet"
      subtitle="Add some income or expenses to see the chart"
    />

    <!-- Chart container — always in DOM so ref is available; hidden until ready -->
    <div v-show="!loading && !isEmpty" ref="chartContainer" class="overflow-hidden"></div>

    <div v-show="!loading && !isEmpty" class="mt-2 flex justify-center gap-4">
      <span class="flex items-center gap-1 text-xs text-ink-gray-5">
        <span class="inline-block h-2 w-2 rounded-full bg-green-500"></span> Income
      </span>
      <span class="flex items-center gap-1 text-xs text-ink-gray-5">
        <span class="inline-block h-2 w-2 rounded-full bg-red-400"></span> Expense
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Chart } from 'frappe-charts'
import EmptyState from '@/components/EmptyState.vue'

const props = defineProps({
  labels:  { type: Array, default: () => [] },
  income:  { type: Array, default: () => [] },
  expense: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const chartContainer = ref(null)
let chartInstance = null

const isEmpty = computed(() =>
  !props.income.some((v) => v > 0) && !props.expense.some((v) => v > 0),
)

function buildChartData() {
  return {
    labels: props.labels,
    datasets: [
      { name: 'Income',  values: props.income  },
      { name: 'Expense', values: props.expense },
    ],
  }
}

function createChart() {
  if (!chartContainer.value || isEmpty.value) return
  chartInstance = new Chart(chartContainer.value, {
    type: 'bar',
    data: buildChartData(),
    colors: ['#22c55e', '#f87171'],
    height: 180,
    axisOptions: { xIsSeries: true },
    barOptions: { spaceRatio: 0.4 },
    tooltipOptions: {
      formatTooltipY: (value) =>
        Number(value || 0).toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }),
    },
  })
}

// Watch for loading → false, then create chart after DOM updates
watch(
  () => props.loading,
  async (isLoading) => {
    if (isLoading) return
    await nextTick()
    if (chartInstance) {
      chartInstance.update(buildChartData())
    } else {
      createChart()
    }
  },
)

// Watch for data changes after chart is created
watch(
  () => [props.labels, props.income, props.expense],
  () => {
    if (props.loading || !chartInstance) return
    chartInstance.update(buildChartData())
  },
  { deep: true },
)
</script>
