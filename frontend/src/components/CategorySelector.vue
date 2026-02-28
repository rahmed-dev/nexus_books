<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div class="fixed inset-0 z-50 bg-black/40" @click="emit('close')" />

    <!-- Bottom sheet -->
    <div
      class="fixed inset-x-0 bottom-0 z-50 flex max-h-[75vh] flex-col rounded-t-2xl bg-surface-white"
      :style="{ paddingBottom: 'env(safe-area-inset-bottom)' }"
    >
      <!-- Drag handle -->
      <div class="flex justify-center pt-3 pb-1">
        <div class="h-1 w-10 rounded-full bg-outline-gray-2" />
      </div>

      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-2">
        <h2 class="text-base font-semibold text-ink-gray-9">Select Category</h2>
        <button
          type="button"
          class="p-1 text-ink-gray-5 active:text-ink-gray-9"
          @click="emit('close')"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Search -->
      <div class="px-4 pb-3">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Search categories…"
          class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          autofocus
        />
      </div>

      <!-- Category grid -->
      <div class="flex-1 overflow-y-auto px-4 pb-4">
        <p v-if="filteredCategories.length === 0" class="py-8 text-center text-sm text-ink-gray-5">
          No categories found
        </p>

        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="category in filteredCategories"
            :key="category.name"
            type="button"
            class="flex flex-col items-center gap-1.5 rounded-xl p-3 text-center transition-transform active:scale-95"
            :class="selectedCategoryId === category.name ? 'ring-2 ring-ink-gray-9' : ''"
            :style="{ backgroundColor: categoryBackground(category) }"
            @click="emit('select', category)"
          >
            <span class="text-2xl leading-none">{{ category.icon || '💰' }}</span>
            <span class="text-xs font-medium leading-tight text-ink-gray-7">
              {{ category.category_name }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCategoryStore } from '@/stores/categories'

const props = defineProps({
  selectedCategoryId: {
    type: String,
    default: null,
  },
  transactionType: {
    type: String,
    default: null, // null = show all active categories
  },
})

const emit = defineEmits(['select', 'close'])

const categoryStore = useCategoryStore()
const searchQuery = ref('')

const filteredCategories = computed(() => {
  const sourceList = props.transactionType
    ? categoryStore.categories.filter(
        (c) => c.category_type === props.transactionType && c.is_active,
      )
    : categoryStore.activeCategories

  if (!searchQuery.value.trim()) return sourceList

  const needle = searchQuery.value.trim().toLowerCase()
  return sourceList.filter((c) => c.category_name.toLowerCase().includes(needle))
})

function categoryBackground(category) {
  if (category.color) return category.color + '22' // 13% opacity
  return category.category_type === 'Income' ? '#dcfce7' : '#fee2e2'
}
</script>
