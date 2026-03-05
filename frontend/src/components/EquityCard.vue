<template>
  <div class="flex items-center justify-between rounded-xl border border-surface-gray-2 bg-surface-white px-4 py-3 shadow-sm">
    <div class="flex items-center gap-3">
      <div
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
        :class="equity >= 0 ? 'bg-emerald-50' : 'bg-red-50'"
      >
        <span
          class="h-5 w-5 [&>svg]:h-full [&>svg]:w-full"
          :class="equity >= 0 ? 'text-emerald-500' : 'text-red-400'"
          v-html="iconSvg"
        />
      </div>
      <div>
        <p class="text-xs text-ink-gray-4">Net worth across all accounts</p>
        <p class="text-sm font-semibold text-ink-gray-7">Equity</p>
      </div>
    </div>

    <div class="text-right">
      <span v-if="loading" class="inline-block h-5 w-20 animate-pulse rounded bg-surface-gray-2" />
      <p v-else class="text-base font-bold" :class="equity >= 0 ? 'text-ink-gray-9' : 'text-red-500'">
        {{ formatCurrency(equity, currencySymbol) }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getIconSvg } from '@/utils/icons'
import { formatCurrency } from '@/utils/currency'

const props = defineProps({
  equity:         { type: Number, default: 0 },
  currencySymbol: { type: String, default: 'Rs.' },
  loading:        { type: Boolean, default: false },
})

const iconSvg = computed(() =>
  getIconSvg(props.equity >= 0 ? 'trending-up' : 'trending-down'),
)
</script>
