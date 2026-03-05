<template>
  <div>
    <!-- Swipeable chart slider -->
    <div
      class="overflow-hidden"
      @touchstart.passive="onTouchStart"
      @touchmove.passive="onTouchMove"
      @touchend.passive="onTouchEnd"
    >
      <!-- Dot indicators — centered above the chart -->
      <div class="mb-3 flex items-center justify-center gap-2">
        <button
          v-for="(_, i) in 2"
          :key="i"
          class="rounded-full transition-all duration-200"
          :class="activeIndex === i ? 'h-2 w-4 bg-surface-gray-7' : 'h-2 w-2 bg-surface-gray-3'"
          @click="activeIndex = i"
        />
      </div>

      <div
        class="flex transition-transform duration-300"
        :style="{ width: '200%', transform: `translateX(-${activeIndex * 50}%)` }"
      >
        <!-- Expense donut -->
        <div class="w-1/2 overflow-hidden">
          <DonutChart
            title="Expense"
            :labels="expenseLabels"
            :amounts="expenseAmounts"
            :colors="expenseColors"
            :loading="loading"
          />
        </div>

        <!-- Income donut -->
        <div class="w-1/2 overflow-hidden">
          <DonutChart
            title="Income"
            :labels="incomeLabels"
            :amounts="incomeAmounts"
            :colors="incomeColors"
            :loading="loading"
          />
        </div>
      </div>
    </div>

    <p class="mt-1 text-center text-xs text-ink-gray-3">
      {{ activeIndex === 0 ? 'Expense' : 'Income' }} by category · swipe to switch
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import DonutChart from '@/components/DonutChart.vue'

defineProps({
  expenseLabels:  { type: Array, default: () => [] },
  expenseAmounts: { type: Array, default: () => [] },
  expenseColors:  { type: Array, default: () => [] },
  incomeLabels:   { type: Array, default: () => [] },
  incomeAmounts:  { type: Array, default: () => [] },
  incomeColors:   { type: Array, default: () => [] },
  loading:        { type: Boolean, default: false },
})

const activeIndex = ref(0)

const SWIPE_THRESHOLD_PX = 40

let touchStartX = 0
let touchStartY = 0

function onTouchStart(event) {
  touchStartX = event.touches[0].clientX
  touchStartY = event.touches[0].clientY
}

function onTouchMove() {}

function onTouchEnd(event) {
  const deltaX = event.changedTouches[0].clientX - touchStartX
  const deltaY = event.changedTouches[0].clientY - touchStartY

  if (Math.abs(deltaY) > Math.abs(deltaX)) return
  if (Math.abs(deltaX) < SWIPE_THRESHOLD_PX) return

  if (deltaX < 0 && activeIndex.value === 0) {
    activeIndex.value = 1
  } else if (deltaX > 0 && activeIndex.value === 1) {
    activeIndex.value = 0
  }
}
</script>
