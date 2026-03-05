<template>
  <div class="relative overflow-hidden">
    <!-- Delete hint background (revealed on swipe left) -->
    <div class="absolute inset-y-0 right-0 flex w-20 items-center justify-center bg-red-500">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    </div>

    <!-- Swipeable card row -->
    <div
      class="relative flex items-center gap-3 bg-surface-white px-4 py-3 active:bg-surface-gray-1"
      :style="{
        transform: `translateX(${swipeOffsetPx}px)`,
        transition: isSwipeInProgress ? 'none' : 'transform 0.2s ease',
      }"
      @click="onTap"
      @touchstart.passive="onTouchStart"
      @touchmove.passive="onTouchMove"
      @touchend.passive="onTouchEnd"
    >
    <!-- Category avatar -->
    <CategoryAvatar
      :icon="resolvedCategory?.icon"
      :color="resolvedCategory?.category_color ?? resolvedCategory?.color"
    />

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
      <span class="text-sm font-semibold" :class="amountColorClass">
        {{ amountPrefix }}{{ formattedAmount }}
      </span>
      <SyncBadge :status="transaction.sync_status" />
    </div>
    </div> <!-- end swipeable row -->
  </div> <!-- end swipe container -->
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import CategoryAvatar from '@/components/CategoryAvatar.vue'
import SyncBadge from '@/components/SyncBadge.vue'

const props = defineProps({
  transaction: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(['edit', 'delete-request'])

// --- Swipe-to-delete ---

const SWIPE_TRIGGER_THRESHOLD_PX = 72
const HORIZONTAL_DOMINANCE_RATIO = 1.5

const swipeOffsetPx = ref(0)
const isSwipeInProgress = ref(false)
let touchStartX = 0
let touchStartY = 0

function onTouchStart(event) {
  touchStartX = event.touches[0].clientX
  touchStartY = event.touches[0].clientY
  isSwipeInProgress.value = true
}

function onTouchMove(event) {
  const deltaX = event.touches[0].clientX - touchStartX
  const deltaY = event.touches[0].clientY - touchStartY

  // Only handle left-swipe that is more horizontal than vertical (not a scroll)
  if (deltaX >= 0) return
  if (Math.abs(deltaY) * HORIZONTAL_DOMINANCE_RATIO > Math.abs(deltaX)) return

  swipeOffsetPx.value = Math.max(deltaX, -120)
}

function onTouchEnd() {
  isSwipeInProgress.value = false
  if (swipeOffsetPx.value < -SWIPE_TRIGGER_THRESHOLD_PX) {
    emit('delete-request', props.transaction)
  }
  swipeOffsetPx.value = 0
}

function onTap() {
  if (Math.abs(swipeOffsetPx.value) > 5) return // mid-swipe snap-back — ignore tap
  emit('edit', props.transaction)
}

const categoryStore = useCategoryStore()

// --- Category display ---

const resolvedCategory = computed(() => {
  // Synced Frappe transactions have category_name + category_icon (not icon)
  // Normalize to always expose `icon` so CategoryAvatar receives the correct prop.
  if (props.transaction.category_name) {
    return {
      category_name: props.transaction.category_name,
      icon: props.transaction.category_icon,
      color: props.transaction.category_color,
    }
  }

  // IDB transactions have category_id — look up from store (store has icon + color)
  if (props.transaction.category_id) {
    return categoryStore.categories.find((c) => c.name === props.transaction.category_id)
  }
  return null
})

const displayCategoryName = computed(
  () => resolvedCategory.value?.category_name ?? props.transaction.category ?? 'Uncategorised',
)

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

</script>
