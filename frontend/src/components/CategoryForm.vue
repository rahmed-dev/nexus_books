<template>
  <BottomSheet
    :title="isEditMode ? 'Edit Category' : 'New Category'"
    max-height="90vh"
    @close="emit('close')"
  >

    <!-- Form body -->
    <div class="px-4 pb-4 pt-2 space-y-4">

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
              ? 'border-surface-gray-7 bg-surface-gray-7 text-white'
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

      <!-- GL Account (hidden for Transfer) -->
      <div v-if="form.category_type !== 'Transfer'">
        <label class="mb-1 block text-xs font-medium text-ink-gray-6">GL Account</label>
        <input
          v-model="form.gl_account"
          type="text"
          placeholder="e.g. Income - Consulting"
          class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        />
        <p class="mt-1 text-xs text-ink-gray-4">Required for Journal Entry posting when no item is set</p>
      </div>

      <!-- Color swatches -->
      <div>
        <label class="mb-2 block text-xs font-medium text-ink-gray-6">Color</label>
        <div class="grid grid-cols-6 gap-2.5">
          <button
            v-for="swatch in colorSwatches"
            :key="swatch"
            type="button"
            class="h-9 w-9 rounded-full border-2 transition-transform active:scale-90"
            :style="{ backgroundColor: swatch }"
            :class="form.color === swatch ? 'border-ink-gray-9 scale-110' : 'border-transparent'"
            @click="form.color = swatch"
          />
          <!-- Clear color -->
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full border-2 border-outline-gray-2 text-ink-gray-4 transition-transform active:scale-90"
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

    <template #footer>
      <div class="px-4 py-3">
        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white transition-opacity active:opacity-80 disabled:opacity-40"
          :disabled="isSaving || !form.category_name.trim() || !form.category_type"
          @click="save"
        >
          {{ isSaving ? 'Saving…' : (isEditMode ? 'Save Changes' : 'Create Category') }}
        </button>
      </div>
    </template>

  </BottomSheet>

  <!-- Icon picker (separate Teleport, controlled independently) -->
  <IconPicker
    v-if="showIconPicker"
    :model-value="form.icon"
    @select="onIconSelected"
    @close="showIconPicker = false"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCategoryStore } from '@/stores/categories'
import BottomSheet from '@/components/BottomSheet.vue'
import IconPicker from '@/components/IconPicker.vue'
import { getIconSvg } from '@/utils/icons'

const props = defineProps({
  category: { type: Object, default: null },
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
  // Reds & Pinks
  '#FF6B6B', '#FF8FA3', '#F472B6', '#E879F9',
  // Oranges & Warm
  '#FB923C', '#FBBF24', '#D4A574', '#E8B89A',
  // Greens
  '#4ADE80', '#34D399', '#86EFAC', '#8B9E7A',
  // Blues & Teals
  '#60A5FA', '#38BDF8', '#22D3EE', '#2DD4BF',
  // Purples & Indigo
  '#818CF8', '#A78BFA', '#C084FC', '#7B6888',
  // Earth & Neutral
  '#94A3B8', '#9CA3AF', '#B5916C', '#78909C',
]

const form = ref({
  category_name: '',
  category_type: 'Expense',
  color: null,
  icon: null,
  gl_account: null,
})

watch(
  () => props.category,
  (category) => {
    if (category) {
      form.value = {
        category_name: category.category_name,
        category_type: category.category_type,
        color: category.color || null,
        icon: category.icon || null,
        gl_account: category.gl_account || null,
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
