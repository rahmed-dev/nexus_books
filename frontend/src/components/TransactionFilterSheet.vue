<template>
  <BottomSheet :is-open="isOpen" title="Filters" @close="emit('close')">

    <div class="px-4 pb-4 pt-2 space-y-6">

      <!-- Period -->
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">Period</p>
        <div class="flex flex-wrap gap-2">
          <FilterChip
            v-for="opt in PERIOD_OPTIONS"
            :key="opt.value"
            :active="localPeriod === opt.value"
            @click="localPeriod = opt.value"
          >
            {{ opt.label }}
          </FilterChip>
        </div>
      </div>

      <!-- Date range — only when Custom is selected -->
      <div v-if="localPeriod === 'custom'" class="space-y-3">
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">From</label>
          <input
            v-model="localFromDate"
            type="date"
            class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          />
        </div>
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">To</label>
          <input
            v-model="localToDate"
            type="date"
            class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          />
        </div>
      </div>

      <!-- Categories -->
      <div>
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">Categories</p>
        <div class="flex flex-wrap gap-2">
          <FilterChip :active="localSelectedCategories.length === 0" @click="localSelectedCategories = []">
            All
          </FilterChip>
          <FilterChip
            v-for="cat in categories"
            :key="cat.name"
            :active="localSelectedCategories.includes(cat.name)"
            @click="toggleCategory(cat.name)"
          >
            <span
              v-if="cat.icon"
              class="mr-1 inline-flex h-3.5 w-3.5 items-center"
              v-html="getCategoryIcon(cat.icon)"
            />
            {{ cat.category_name }}
          </FilterChip>
        </div>
      </div>

    </div>

    <template #footer>
      <div class="px-4 py-3">
        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white active:bg-surface-gray-6"
          @click="onApply"
        >
          Apply
        </button>
      </div>
    </template>

  </BottomSheet>
</template>

<script setup>
import { ref, watch } from 'vue'
import BottomSheet from '@/components/BottomSheet.vue'
import FilterChip from '@/components/FilterChip.vue'
import { getIconSvg } from '@/utils/icons.js'

const props = defineProps({
  isOpen: Boolean,
  categories: { type: Array, default: () => [] },
  filter: {
    type: Object,
    default: () => ({ period: 'all', fromDate: '', toDate: '', selectedCategories: [] }),
  },
})

const emit = defineEmits(['close', 'apply'])

const PERIOD_OPTIONS = [
  { value: 'month', label: 'This Month' },
  { value: 'last_month', label: 'Last Month' },
  { value: 'year', label: 'This Year' },
  { value: 'all', label: 'All' },
  { value: 'custom', label: 'Custom' },
]

const localPeriod = ref(props.filter.period)
const localFromDate = ref(props.filter.fromDate || '')
const localToDate = ref(props.filter.toDate || '')
const localSelectedCategories = ref([...props.filter.selectedCategories])

watch(
  () => props.isOpen,
  (opened) => {
    if (opened) {
      localPeriod.value = props.filter.period
      localFromDate.value = props.filter.fromDate || ''
      localToDate.value = props.filter.toDate || ''
      localSelectedCategories.value = [...props.filter.selectedCategories]
    }
  },
)

function getCategoryIcon(iconName) {
  const svg = getIconSvg(iconName)
  return svg ? svg.replace('width="24"', 'width="14"').replace('height="24"', 'height="14"') : ''
}

function toggleCategory(categoryName) {
  const idx = localSelectedCategories.value.indexOf(categoryName)
  if (idx === -1) {
    localSelectedCategories.value.push(categoryName)
  } else {
    localSelectedCategories.value.splice(idx, 1)
  }
}

function onApply() {
  emit('apply', {
    period: localPeriod.value,
    fromDate: localPeriod.value === 'custom' ? localFromDate.value : '',
    toDate: localPeriod.value === 'custom' ? localToDate.value : '',
    selectedCategories: [...localSelectedCategories.value],
  })
}
</script>
