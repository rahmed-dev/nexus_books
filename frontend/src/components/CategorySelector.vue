<template>
  <BottomSheet title="Select Category" max-height="75vh" @close="emit('close')">

    <!-- Type filter chips — only shown when not locked to a specific type -->
    <div v-if="!transactionType" class="flex gap-2 overflow-x-auto px-4 pb-3 pt-1 no-scrollbar">
      <FilterChip
        v-for="option in TYPE_OPTIONS"
        :key="option.value"
        :active="activeTypeFilter === option.value"
        @click="activeTypeFilter = option.value"
      >
        {{ option.label }}
      </FilterChip>
    </div>

    <!-- Search -->
    <div class="px-4 pb-3" :class="transactionType ? 'pt-1' : ''">
      <input
        v-model="searchQuery"
        type="search"
        placeholder="Search categories…"
        class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        autofocus
      />
    </div>

    <!-- Category grid -->
    <div class="px-4 pb-4">
      <p v-if="filteredCategories.length === 0" class="py-8 text-center text-sm text-ink-gray-5">
        No categories found
      </p>
      <div class="grid grid-cols-3 gap-2">
        <CategoryChip
          v-for="category in filteredCategories"
          :key="category.name"
          :label="category.category_name"
          :icon="category.icon"
          :color="category.color"
          :category-type="category.category_type"
          :selected="selectedCategoryId === category.name"
          @click="emit('select', category)"
        />
      </div>
    </div>

  </BottomSheet>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import BottomSheet from '@/components/BottomSheet.vue'
import CategoryChip from '@/components/CategoryChip.vue'
import FilterChip from '@/components/FilterChip.vue'

const TYPE_OPTIONS = [
  { value: 'Expense', label: 'Expense' },
  { value: 'Income', label: 'Income' },
  { value: 'Transfer', label: 'Transfer' },
]

const props = defineProps({
  selectedCategoryId: { type: String, default: null },
  // When passed from edit form, locks the filter to this type.
  // When null (FAB flow), the user can switch type via filter chips.
  transactionType: { type: String, default: null },
})

const emit = defineEmits(['select', 'close'])

const categoryStore = useCategoryStore()
const searchQuery = ref('')
// Default to Expense for the FAB quick-add flow
const activeTypeFilter = ref('Expense')

const filteredCategories = computed(() => {
  const effectiveType = props.transactionType ?? activeTypeFilter.value

  const sourceList = effectiveType
    ? categoryStore.categories.filter((c) => c.category_type === effectiveType && c.is_active)
    : categoryStore.activeCategories

  if (!searchQuery.value.trim()) return sourceList

  const needle = searchQuery.value.trim().toLowerCase()
  return sourceList.filter((c) => c.category_name.toLowerCase().includes(needle))
})
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
</style>
