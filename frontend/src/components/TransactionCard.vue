<template>
  <div class="flex items-center gap-3 px-4 py-3 active:bg-surface-gray-1">
    <!-- Category color dot + type icon -->
    <div
      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
      :style="{ backgroundColor: categoryBackground }"
    >
      <!-- Income: arrow up -->
      <svg
        v-if="transaction.transaction_type === 'Income'"
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 text-green-700"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
      </svg>
      <!-- Expense: arrow down -->
      <svg
        v-else-if="transaction.transaction_type === 'Expense'"
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 text-red-700"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
      </svg>
      <!-- Transfer: swap -->
      <svg
        v-else
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 text-blue-700"
        fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"
      >
        <path stroke-linecap="round" stroke-linejoin="round" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4" />
      </svg>
    </div>

    <!-- Category + description -->
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-medium text-ink-gray-9">
        {{ displayCategoryName }}
      </p>
      <p v-if="transaction.sync_error" class="truncate text-xs text-red-500">
        {{ transaction.sync_error }}
      </p>
      <p v-else-if="transaction.description" class="truncate text-xs text-ink-gray-5">
        {{ transaction.description }}
      </p>
      <p v-else class="text-xs text-ink-gray-4">
        {{ formattedDate }}
      </p>
    </div>

    <!-- Amount + sync badge -->
    <div class="flex shrink-0 flex-col items-end gap-1">
      <span
        class="text-sm font-semibold"
        :class="amountColorClass"
      >
        {{ amountPrefix }}{{ formattedAmount }}
      </span>
      <span
        v-if="syncBadgeLabel"
        class="rounded-full px-1.5 py-0.5 text-xs font-medium"
        :class="syncBadgeClass"
      >
        {{ syncBadgeLabel }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useCategoryStore } from '@/stores/categories'

const props = defineProps({
  transaction: {
    type: Object,
    required: true,
  },
})

const categoryStore = useCategoryStore()

// --- Category display ---

const resolvedCategory = computed(() => {
  // Frappe transactions already have category_name + category_color
  if (props.transaction.category_name) return props.transaction

  // IDB transactions have category_id — look up from store
  if (props.transaction.category_id) {
    return categoryStore.categories.find((c) => c.name === props.transaction.category_id)
  }
  return null
})

const displayCategoryName = computed(
  () => resolvedCategory.value?.category_name ?? props.transaction.category ?? 'Uncategorised',
)

const categoryBackground = computed(() => {
  const color = resolvedCategory.value?.category_color ?? resolvedCategory.value?.color
  if (!color) {
    return props.transaction.transaction_type === 'Income'
      ? '#dcfce7'
      : props.transaction.transaction_type === 'Expense'
        ? '#fee2e2'
        : '#dbeafe'
  }
  // Apply 20% opacity to the category hex color for a soft background
  return color + '33'
})

// --- Amount display ---

const formattedAmount = computed(() =>
  Number(props.transaction.amount || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }),
)

const amountPrefix = computed(() =>
  props.transaction.transaction_type === 'Income' ? '+' : '-',
)

const amountColorClass = computed(() =>
  props.transaction.transaction_type === 'Income' ? 'text-green-600' : 'text-ink-gray-9',
)

// --- Date display ---

const formattedDate = computed(() => {
  const raw = props.transaction.date || props.transaction.created_at
  if (!raw) return ''
  return new Date(raw).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
})

// --- Sync badge (IDB transactions only) ---

const SYNC_BADGE_CONFIG = {
  pending: { label: 'Pending', classes: 'bg-yellow-100 text-yellow-800' },
  syncing: { label: 'Syncing…', classes: 'bg-blue-100 text-blue-800' },
  failed: { label: 'Failed', classes: 'bg-red-100 text-red-800' },
  synced: null, // no badge needed once synced
}

const syncBadgeConfig = computed(
  () => SYNC_BADGE_CONFIG[props.transaction.sync_status] ?? null,
)

const syncBadgeLabel = computed(() => syncBadgeConfig.value?.label ?? null)
const syncBadgeClass = computed(() => syncBadgeConfig.value?.classes ?? '')
</script>
