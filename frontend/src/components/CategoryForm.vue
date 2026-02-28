<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <div class="fixed inset-0 z-50 bg-black/40" @click="emit('close')" />

    <!-- Bottom sheet -->
    <div
      class="fixed inset-x-0 bottom-0 z-50 flex max-h-[90vh] flex-col rounded-t-2xl bg-surface-white"
      :style="{ paddingBottom: 'env(safe-area-inset-bottom)' }"
    >
      <!-- Drag handle -->
      <div class="flex justify-center pt-3 pb-1">
        <div class="h-1 w-10 rounded-full bg-outline-gray-2" />
      </div>

      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-2">
        <h2 class="text-base font-semibold text-ink-gray-9">
          {{ isEditMode ? 'Edit Category' : 'New Category' }}
        </h2>
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

      <!-- Form body -->
      <div class="flex-1 overflow-y-auto px-4 pb-4 space-y-4">

        <!-- Category name -->
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">Name *</label>
          <input
            v-model="form.category_name"
            type="text"
            placeholder="e.g. Groceries"
            class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
          />
        </div>

        <!-- Type selector -->
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">Type *</label>
          <div class="flex gap-2">
            <button
              v-for="typeOption in typeOptions"
              :key="typeOption.value"
              type="button"
              class="flex-1 rounded-xl border py-2 text-sm font-medium transition-colors"
              :class="form.category_type === typeOption.value
                ? 'border-ink-gray-9 bg-ink-gray-9 text-surface-white'
                : 'border-outline-gray-2 bg-surface-gray-1 text-ink-gray-7'"
              @click="form.category_type = typeOption.value"
            >
              {{ typeOption.label }}
            </button>
          </div>
        </div>

        <!-- Icon picker trigger -->
        <div>
          <label class="mb-1 block text-xs font-medium text-ink-gray-6">Icon</label>
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-left"
            @click="showIconPicker = true"
          >
            <span
              v-if="form.icon"
              class="h-6 w-6 shrink-0 text-ink-gray-8 [&>svg]:h-full [&>svg]:w-full"
              v-html="selectedIconSvg"
            />
            <span v-else class="h-6 w-6 shrink-0 rounded bg-surface-gray-2" />
            <span class="text-sm" :class="form.icon ? 'text-ink-gray-9' : 'text-ink-gray-4'">
              {{ form.icon || 'Choose an icon…' }}
            </span>
          </button>
        </div>

        <!-- Color swatches -->
        <div>
          <label class="mb-2 block text-xs font-medium text-ink-gray-6">Color</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="swatch in colorSwatches"
              :key="swatch"
              type="button"
              class="h-8 w-8 rounded-full border-2 transition-transform active:scale-90"
              :style="{ backgroundColor: swatch }"
              :class="form.color === swatch ? 'border-ink-gray-9 scale-110' : 'border-transparent'"
              @click="form.color = swatch"
            />
            <!-- Clear color -->
            <button
              type="button"
              class="flex h-8 w-8 items-center justify-center rounded-full border-2 border-outline-gray-2 text-ink-gray-4 transition-transform active:scale-90"
              :class="!form.color ? 'border-ink-gray-9' : ''"
              @click="form.color = null"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Save button -->
      <div class="px-4 py-3 border-t border-outline-gray-1">
        <button
          type="button"
          class="w-full rounded-xl bg-ink-gray-9 py-3 text-sm font-semibold text-surface-white transition-opacity active:opacity-80 disabled:opacity-40"
          :disabled="isSaving || !form.category_name.trim() || !form.category_type"
          @click="save"
        >
          {{ isSaving ? 'Saving…' : (isEditMode ? 'Save Changes' : 'Create Category') }}
        </button>
      </div>
    </div>

    <!-- Icon picker (nested teleport) -->
    <IconPicker
      v-if="showIconPicker"
      :model-value="form.icon"
      @select="onIconSelected"
      @close="showIconPicker = false"
    />
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import IconPicker from '@/components/IconPicker.vue'
import { getIconSvg } from '@/utils/icons'

const props = defineProps({
  /** Existing category object to edit, or null to create */
  category: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['close', 'saved'])

const categoryStore = useCategoryStore()

const isEditMode = computed(() => !!props.category)
const isSaving = ref(false)
const showIconPicker = ref(false)

const typeOptions = [
  { value: 'Income', label: 'Income' },
  { value: 'Expense', label: 'Expense' },
  { value: 'Transfer', label: 'Transfer' },
]

const colorSwatches = [
  '#ef4444', '#f97316', '#eab308', '#22c55e',
  '#14b8a6', '#3b82f6', '#8b5cf6', '#ec4899',
  '#64748b', '#171717',
]

const form = ref({
  category_name: '',
  category_type: 'Expense',
  color: null,
  icon: null,
})

// Pre-fill form when editing
watch(
  () => props.category,
  (category) => {
    if (category) {
      form.value = {
        category_name: category.category_name,
        category_type: category.category_type,
        color: category.color || null,
        icon: category.icon || null,
      }
    }
  },
  { immediate: true },
)

const selectedIconSvg = computed(() => getIconSvg(form.value.icon))

function onIconSelected(iconName) {
  form.value.icon = iconName
  showIconPicker.value = false
}

async function save() {
  if (!form.value.category_name.trim() || !form.value.category_type) return

  isSaving.value = true
  try {
    if (isEditMode.value) {
      await categoryStore.updateCategory(props.category.name, form.value)
    } else {
      await categoryStore.createCategory(form.value)
    }
    emit('saved')
    emit('close')
  } finally {
    isSaving.value = false
  }
}
</script>
