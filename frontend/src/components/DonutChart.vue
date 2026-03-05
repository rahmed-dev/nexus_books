<template>
  <div>
    <!-- Loading skeleton -->
    <div v-show="loading" class="flex h-44 items-center justify-center">
      <div class="h-32 w-32 animate-pulse rounded-full bg-surface-gray-3"></div>
    </div>

    <!-- Empty state -->
    <EmptyState
      v-show="!loading && isEmpty"
      :title="`No ${title.toLowerCase()} this month`"
    />

    <!-- Chart container — always in DOM so ref is available -->
    <div v-show="!loading && !isEmpty" ref="chartContainer" class="overflow-hidden"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Chart } from 'frappe-charts'
import EmptyState from '@/components/EmptyState.vue'

const props = defineProps({
  title:   { type: String, required: true },
  labels:  { type: Array,  default: () => [] },
  amounts: { type: Array,  default: () => [] },
  colors:  { type: Array,  default: () => [] },
  loading: { type: Boolean, default: false },
})

const chartContainer = ref(null)
let chartInstance = null
const lastColors = ref([])

const isEmpty = computed(() => !props.amounts.some((v) => v > 0))

function buildChartData() {
  return {
    labels: props.labels,
    datasets: [{ values: props.amounts }],
  }
}

function colorsChanged(newColors) {
  if (newColors.length !== lastColors.value.length) return true
  return newColors.some((color, index) => color !== lastColors.value[index])
}

function destroyChart() {
  if (chartContainer.value) chartContainer.value.innerHTML = ''
  chartInstance = null
}

function createChart() {
  if (!chartContainer.value || isEmpty.value) return
  const activeColors = props.colors.length ? props.colors : ['#94a3b8']
  chartInstance = new Chart(chartContainer.value, {
    type: 'donut',
    data: buildChartData(),
    colors: activeColors,
    height: 200,
    tooltipOptions: {
      formatTooltipY: (value) =>
        Number(value || 0).toLocaleString('en-US', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        }),
    },
  })
  lastColors.value = [...activeColors]
}

watch(
  () => props.loading,
  async (isLoading) => {
    if (isLoading) return
    await nextTick()
    if (chartInstance) {
      // frappe-charts update() does not support color changes — recreate when needed
      if (colorsChanged(props.colors)) {
        destroyChart()
        createChart()
      } else {
        chartInstance.update(buildChartData())
      }
    } else {
      createChart()
    }
  },
)

watch(
  () => [props.labels, props.amounts, props.colors],
  () => {
    if (props.loading || !chartInstance) return
    if (colorsChanged(props.colors)) {
      destroyChart()
      createChart()
    } else {
      chartInstance.update(buildChartData())
    }
  },
  { deep: true },
)
</script>
