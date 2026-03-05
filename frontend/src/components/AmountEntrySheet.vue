<template>
  <BottomSheet :title="null" @close="emit('close')">

    <div class="flex flex-col px-4 pt-2 pb-4 gap-4">

      <!-- Transaction type -->
      <SegmentedControl
        v-model="transactionType"
        :options="TRANSACTION_TYPE_OPTIONS"
      />

      <!-- Selected category (tap to go back and change) -->
      <button
        type="button"
        class="flex items-center gap-3 rounded-xl bg-surface-gray-1 px-4 py-3 active:bg-surface-gray-2"
        @click="emit('change-category')"
      >
        <CategoryAvatar :icon="selectedCategory?.icon" :color="selectedCategory?.color" size="md" />
        <div class="min-w-0 flex-1 text-left">
          <p class="truncate text-sm font-medium text-ink-gray-9">{{ selectedCategory?.category_name ?? 'No category' }}</p>
          <p class="text-xs text-ink-gray-5">Tap to change</p>
        </div>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <!-- Amount display -->
      <div class="text-center py-2">
        <span class="text-4xl font-bold tracking-tight text-ink-gray-9">
          {{ amountDisplay }}
        </span>
      </div>

      <!-- Date row -->
      <div class="flex items-center justify-between rounded-xl border border-outline-gray-2 px-4 py-2.5">
        <span class="text-sm text-ink-gray-6">Date</span>
        <input
          v-model="selectedDate"
          type="date"
          class="text-sm font-medium text-ink-gray-9 bg-transparent border-none outline-none"
        />
      </div>

      <!-- Account chips — horizontal scroll -->
      <div class="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
        <FilterChip
          v-for="account in accountStore.accounts"
          :key="account.name"
          :active="selectedAccountName === account.name"
          @click="selectedAccountName = account.name"
        >
          {{ account.account_name }}
        </FilterChip>
      </div>

      <!-- Custom numpad -->
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="key in NUMPAD_KEYS"
          :key="key.label"
          type="button"
          class="flex h-14 items-center justify-center rounded-xl bg-surface-gray-1 text-lg font-medium text-ink-gray-9 active:bg-surface-gray-3 disabled:opacity-30"
          :disabled="key.action === 'decimal' && amountString.includes('.')"
          @click="onNumpadKey(key)"
        >
          <template v-if="key.action === 'backspace'">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M3 12l6.414 6.414a2 2 0 001.414.586H19a2 2 0 002-2V7a2 2 0 00-2-2h-8.172a2 2 0 00-1.414.586L3 12z" />
            </svg>
          </template>
          <template v-else>{{ key.label }}</template>
        </button>
      </div>

      <!-- Save button -->
      <button
        type="button"
        class="w-full rounded-xl bg-surface-gray-7 py-3.5 text-sm font-semibold text-white active:bg-surface-gray-6 disabled:opacity-50"
        :disabled="!canSave || isSaving"
        @click="saveTransaction"
      >
        {{ isSaving ? 'Saving…' : 'Add Transaction' }}
      </button>

      <p v-if="saveError" class="text-center text-xs text-red-500">{{ saveError }}</p>

    </div>

  </BottomSheet>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import { useTransactionStore } from '@/stores/transactions'
import { useSyncStore } from '@/stores/sync'
import BottomSheet from '@/components/BottomSheet.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import CategoryAvatar from '@/components/CategoryAvatar.vue'
import FilterChip from '@/components/FilterChip.vue'

const props = defineProps({
  selectedCategory: { type: Object, default: null },
  initialType: { type: String, default: 'Expense' },
})

const emit = defineEmits(['close', 'saved', 'change-category'])

const accountStore = useAccountStore()
const transactionStore = useTransactionStore()
const syncStore = useSyncStore()

const TRANSACTION_TYPE_OPTIONS = [
  { value: 'Expense', label: 'Expense' },
  { value: 'Income', label: 'Income' },
  { value: 'Transfer', label: 'Transfer' },
]

const NUMPAD_KEYS = [
  { label: '1', action: 'digit' },
  { label: '2', action: 'digit' },
  { label: '3', action: 'digit' },
  { label: '4', action: 'digit' },
  { label: '5', action: 'digit' },
  { label: '6', action: 'digit' },
  { label: '7', action: 'digit' },
  { label: '8', action: 'digit' },
  { label: '9', action: 'digit' },
  { label: '.', action: 'decimal' },
  { label: '0', action: 'digit' },
  { label: '⌫', action: 'backspace' },
]

const transactionType = ref(props.initialType)
const amountString = ref('')
const selectedDate = ref(todayDateString())
const selectedAccountName = ref(accountStore.defaultAccount?.name ?? '')
const isSaving = ref(false)
const saveError = ref(null)

const amountDisplay = computed(() => {
  if (!amountString.value) return '0.00'
  const num = parseFloat(amountString.value)
  return isNaN(num) ? '0.00' : amountString.value
})

const parsedAmount = computed(() => parseFloat(amountString.value) || 0)

const canSave = computed(
  () => parsedAmount.value > 0 && !!selectedAccountName.value,
)

function onNumpadKey(key) {
  if (key.action === 'backspace') {
    amountString.value = amountString.value.slice(0, -1)
    return
  }
  if (key.action === 'decimal') {
    if (!amountString.value.includes('.')) {
      amountString.value = amountString.value ? amountString.value + '.' : '0.'
    }
    return
  }
  // digit — limit to 2 decimal places
  if (amountString.value.includes('.')) {
    const decimalPart = amountString.value.split('.')[1]
    if (decimalPart.length >= 2) return
  }
  amountString.value += key.label
}

async function saveTransaction() {
  if (!canSave.value) return
  isSaving.value = true
  saveError.value = null
  try {
    await transactionStore.addTransaction({
      transaction_type: transactionType.value,
      amount: parsedAmount.value,
      date: selectedDate.value,
      category_id: props.selectedCategory?.name ?? null,
      category_label: props.selectedCategory?.category_name ?? null,
      nexus_account: selectedAccountName.value,
    })
    await syncStore.syncAll()
    emit('saved')
    emit('close')
  } catch {
    saveError.value = 'Failed to save. Please try again.'
  } finally {
    isSaving.value = false
  }
}

function todayDateString() {
  const now = new Date()
  const yyyy = now.getFullYear()
  const mm = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
