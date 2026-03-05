<template>
  <div class="flex flex-col pb-24">

    <PageHeader title="Categories" back-to="/settings" />

    <!-- FAB: add category -->
    <FAB label="Add category" @click="openCreateForm" />

    <!-- Filter chips -->
    <div class="flex gap-2 overflow-x-auto px-4 pb-3 scrollbar-hide">
      <FilterChip
        v-for="filter in filterOptions"
        :key="filter.value"
        :active="activeFilter === filter.value"
        @click="activeFilter = filter.value"
      >
        {{ filter.label }}
        <span class="ml-1 opacity-70">{{ filterCount(filter.value) }}</span>
      </FilterChip>
    </div>

    <!-- Loading -->
    <div v-if="categoryStore.isLoading" class="py-16 text-center text-sm text-ink-gray-5">
      Loading…
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else-if="!filteredCategories.length"
      :title="`No ${activeFilter === 'All' ? '' : activeFilter.toLowerCase() + ' '}categories yet`"
      subtitle="Tap + New to add one"
    />

    <!-- Category rows -->
    <div v-else>
      <div
        v-for="category in filteredCategories"
        :key="category.name"
        class="flex items-center gap-3 px-4 py-3 active:bg-surface-gray-1"
        :class="{ 'opacity-40': !category.is_active }"
        @click="openEditForm(category)"
      >
        <!-- Icon -->
        <CategoryAvatar :icon="category.icon" :color="category.color" />

        <!-- Name + type badge (shown only in All view) -->
        <div class="flex-1 min-w-0">
          <p class="truncate text-sm font-medium text-ink-gray-9">
            {{ category.category_name }}
          </p>
          <p v-if="activeFilter === 'All'" class="text-xs text-ink-gray-5">
            {{ category.category_type }}
          </p>
        </div>

        <!-- Active toggle -->
        <button
          type="button"
          class="shrink-0 rounded-lg px-2.5 py-1 text-xs font-medium transition-colors"
          :class="category.is_active
            ? 'bg-green-100 text-green-700'
            : 'bg-surface-gray-2 text-ink-gray-5'"
          @click.stop="toggleActive(category)"
        >
          {{ category.is_active ? 'Active' : 'Inactive' }}
        </button>
      </div>
    </div>

    <!-- Category form sheet -->
    <CategoryForm
      v-if="showForm"
      :category="editingCategory"
      @close="closeForm"
      @saved="onSaved"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import CategoryForm from '@/components/CategoryForm.vue'
import FAB from '@/components/FAB.vue'
import PageHeader from '@/components/PageHeader.vue'
import FilterChip from '@/components/FilterChip.vue'
import CategoryAvatar from '@/components/CategoryAvatar.vue'
import EmptyState from '@/components/EmptyState.vue'

const categoryStore = useCategoryStore()

const showForm = ref(false)
const editingCategory = ref(null)
const activeFilter = ref('All')

const filterOptions = [
  { value: 'All', label: 'All' },
  { value: 'Income', label: 'Income' },
  { value: 'Expense', label: 'Expense' },
  { value: 'Transfer', label: 'Transfer' },
]

const filteredCategories = computed(() => {
  const all = categoryStore.categories
  if (activeFilter.value === 'All') return all
  return all.filter((c) => c.category_type === activeFilter.value)
})

function filterCount(filterValue) {
  if (filterValue === 'All') return categoryStore.categories.length
  return categoryStore.categories.filter((c) => c.category_type === filterValue).length
}

function openCreateForm() {
  editingCategory.value = null
  showForm.value = true
}

function openEditForm(category) {
  editingCategory.value = category
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editingCategory.value = null
}

async function onSaved() {
  await categoryStore.loadCategories()
}

async function toggleActive(category) {
  await categoryStore.toggleActive(category.name)
}

onMounted(() => {
  categoryStore.loadCategories()
})
</script>
