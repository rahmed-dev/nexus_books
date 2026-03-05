<template>
  <div class="grid grid-cols-3 divide-x divide-surface-gray-2 rounded-xl bg-surface-gray-1 px-2 py-3">
    <div class="flex flex-col items-center gap-0.5 px-2">
      <span class="text-xs text-ink-gray-4">Balance</span>
      <span v-if="loading" class="h-5 w-16 animate-pulse rounded bg-surface-gray-3"></span>
      <span v-else class="text-sm font-semibold text-ink-gray-9">{{ fmt(balance) }}</span>
    </div>

    <div class="flex flex-col items-center gap-0.5 px-2">
      <span class="text-xs text-ink-gray-4">Income</span>
      <span v-if="loading" class="h-5 w-14 animate-pulse rounded bg-surface-gray-3"></span>
      <span v-else class="text-sm font-semibold text-green-600">{{ fmt(income) }}</span>
    </div>

    <div class="flex flex-col items-center gap-0.5 px-2">
      <span class="text-xs text-ink-gray-4">Expense</span>
      <span v-if="loading" class="h-5 w-14 animate-pulse rounded bg-surface-gray-3"></span>
      <span v-else class="text-sm font-semibold text-red-500">{{ fmt(expense) }}</span>
    </div>
  </div>
</template>

<script setup>
import { formatCurrency } from '@/utils/currency'

const props = defineProps({
  balance:        { type: Number, default: 0 },
  income:         { type: Number, default: 0 },
  expense:        { type: Number, default: 0 },
  currencySymbol: { type: String, default: 'Rs.' },
  loading:        { type: Boolean, default: false },
})

function fmt(value) {
  return formatCurrency(value, props.currencySymbol)
}
</script>
