<template>
  <Teleport to="body">
    <!-- Fade backdrop -->
    <Transition name="fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/40"
        @click="close"
      />
    </Transition>

    <!-- Slide-up sheet -->
    <Transition name="slide-up">
      <div
        v-if="isOpen"
        class="fixed inset-x-0 bottom-0 z-50 flex max-h-[92vh] flex-col rounded-t-2xl bg-surface-white"
        :style="{ paddingBottom: 'env(safe-area-inset-bottom)' }"
      >
        <!-- Drag handle -->
        <div class="flex justify-center pt-3 pb-1">
          <div class="h-1 w-10 rounded-full bg-outline-gray-2" />
        </div>

        <!-- Header -->
        <div class="flex items-center justify-between px-4 py-2">
          <h2 class="text-base font-semibold text-ink-gray-9">
            {{ transaction ? 'Edit Transaction' : 'New Transaction' }}
          </h2>
          <button
            type="button"
            class="p-1 text-ink-gray-5 active:text-ink-gray-9"
            @click="close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Scrollable form body -->
        <div class="flex-1 overflow-y-auto px-4 pb-6">
          <!-- Transaction type tabs -->
          <div class="mb-5 mt-2 grid grid-cols-3 gap-1 rounded-xl bg-surface-gray-1 p-1">
            <button
              v-for="txnType in TRANSACTION_TYPES"
              :key="txnType.value"
              type="button"
              class="rounded-lg py-2 text-sm font-medium transition-colors"
              :class="
                form.transaction_type === txnType.value
                  ? 'bg-surface-white text-ink-gray-9 shadow-sm'
                  : 'text-ink-gray-5'
              "
              @click="onTypeChange(txnType.value)"
            >
              {{ txnType.label }}
            </button>
          </div>

          <!-- Amount -->
          <div class="mb-4">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">Amount</label>
            <input
              v-model="form.amount"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
              inputmode="decimal"
              class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-3xl font-bold tracking-tight text-ink-gray-9 placeholder-ink-gray-3 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
            />
          </div>

          <!-- Date -->
          <div class="mb-4">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">Date</label>
            <Input v-model="form.date" type="date" class="w-full" />
          </div>

          <!-- Category -->
          <div class="mb-4">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">Category</label>
            <button
              type="button"
              class="flex w-full items-center justify-between rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm"
              @click="showCategorySelector = true"
            >
              <span :class="form.category_id ? 'text-ink-gray-9' : 'text-ink-gray-4'">
                {{ form.category_label || 'Select category…' }}
              </span>
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>

          <!-- Party: Customer for Income, Supplier for Expense, hidden for Transfer -->
          <div v-if="form.transaction_type !== 'Transfer'" class="mb-4">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">
              {{ form.transaction_type === 'Income' ? 'Customer' : 'Supplier' }}
              <span class="font-normal text-ink-gray-4">(optional)</span>
            </label>
            <PartySelector
              v-model="activePartyId"
              :party-type="form.transaction_type === 'Income' ? 'Customer' : 'Supplier'"
            />
          </div>

          <!-- Description -->
          <div class="mb-4">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">
              Description
              <span class="font-normal text-ink-gray-4">(optional)</span>
            </label>
            <textarea
              v-model="form.description"
              rows="2"
              placeholder="Add a note…"
              class="w-full resize-none rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
            />
          </div>

          <!-- Tax toggle + amount -->
          <div class="mb-4">
            <div class="flex items-center justify-between">
              <label class="text-xs font-medium text-ink-gray-6">Include tax</label>
              <button
                type="button"
                role="switch"
                :aria-checked="includeTax"
                class="relative h-5 w-9 rounded-full transition-colors"
                :class="includeTax ? 'bg-ink-gray-9' : 'bg-outline-gray-2'"
                @click="includeTax = !includeTax"
              >
                <span
                  class="absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-transform"
                  :class="includeTax ? 'translate-x-4' : 'translate-x-0.5'"
                />
              </button>
            </div>
            <div v-if="includeTax" class="mt-2">
              <Input
                v-model="form.tax_amount"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                class="w-full"
              />
            </div>
          </div>

          <!-- Receipt photo -->
          <div class="mb-6">
            <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">
              Receipt photo
              <span class="font-normal text-ink-gray-4">(optional)</span>
            </label>

            <div v-if="receiptPreviewUrl" class="relative mb-2 inline-block">
              <img
                :src="receiptPreviewUrl"
                alt="Receipt preview"
                class="h-24 w-24 rounded-xl object-cover"
              />
              <button
                type="button"
                class="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-ink-gray-9 text-white"
                @click="clearReceiptPhoto"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <label class="flex cursor-pointer items-center gap-2 rounded-xl border border-dashed border-outline-gray-2 px-4 py-3 text-sm text-ink-gray-5 active:bg-surface-gray-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ receiptPreviewUrl ? 'Change photo' : 'Add photo' }}
              <input
                type="file"
                accept="image/*"
                capture="environment"
                class="sr-only"
                @change="onReceiptFileSelected"
              />
            </label>

            <p v-if="photoError" class="mt-1 text-xs text-red-500">{{ photoError }}</p>
          </div>

          <!-- Save button -->
          <Button
            variant="solid"
            class="w-full"
            :loading="isSaving"
            @click="saveTransaction"
          >
            {{ transaction ? 'Save changes' : 'Add transaction' }}
          </Button>

          <p v-if="saveError" class="mt-2 text-center text-xs text-red-500">{{ saveError }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>

  <!-- CategorySelector has its own internal Teleport — rendered outside the sheet Teleport -->
  <CategorySelector
    v-if="showCategorySelector"
    :selected-category-id="form.category_id"
    :transaction-type="form.transaction_type"
    @select="onCategorySelected"
    @close="showCategorySelector = false"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useTransactionStore } from '@/stores/transactions'
import { useSyncStore } from '@/stores/sync'
import CategorySelector from '@/components/CategorySelector.vue'
import PartySelector from '@/components/PartySelector.vue'
import { usePhotoCompressor } from '@/composables/usePhotoCompressor'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false,
  },
  transaction: {
    type: Object,
    default: null, // null = Add mode, Object = Edit mode
  },
})

const emit = defineEmits(['close', 'saved'])

const transactionStore = useTransactionStore()
const syncStore = useSyncStore()
const { compressFile } = usePhotoCompressor()

const TRANSACTION_TYPES = [
  { value: 'Income', label: 'Income' },
  { value: 'Expense', label: 'Expense' },
  { value: 'Transfer', label: 'Transfer' },
]

// --- Form state ---

const form = ref(buildEmptyForm())
const includeTax = ref(false)
const showCategorySelector = ref(false)
const receiptPreviewUrl = ref(null)
const receiptBlob = ref(null)
const receiptFilename = ref(null)
const photoError = ref(null)
const isSaving = ref(false)
const saveError = ref(null)

// Delegate party binding to the correct ID field based on transaction type
const activePartyId = computed({
  get() {
    return form.value.transaction_type === 'Income'
      ? form.value.customer_id
      : form.value.supplier_id
  },
  set(selectedPartyId) {
    if (form.value.transaction_type === 'Income') {
      form.value.customer_id = selectedPartyId
    } else {
      form.value.supplier_id = selectedPartyId
    }
  },
})

// --- Lifecycle ---

watch(
  () => props.isOpen,
  (isNowOpen) => {
    if (isNowOpen) {
      initializeForm()
    }
  },
)

// --- Initialization ---

function buildEmptyForm() {
  return {
    transaction_type: 'Expense',
    amount: '',
    date: todayDateString(),
    category_id: null,
    category_label: null,
    customer_id: null,
    supplier_id: null,
    payment_account_id: '',
    description: '',
    tax_amount: '',
  }
}

function todayDateString() {
  return new Date().toISOString().split('T')[0]
}

async function initializeForm() {
  resetFormState()
  if (props.transaction) {
    prefillFormForEdit(props.transaction)
  } else {
    await loadDefaultPaymentAccount()
  }
}

function resetFormState() {
  form.value = buildEmptyForm()
  includeTax.value = false
  showCategorySelector.value = false
  receiptPreviewUrl.value = null
  receiptBlob.value = null
  receiptFilename.value = null
  photoError.value = null
  saveError.value = null
  isSaving.value = false
}

function prefillFormForEdit(existingTransaction) {
  form.value = {
    transaction_type: existingTransaction.transaction_type || 'Expense',
    amount: existingTransaction.amount || '',
    date: existingTransaction.date || todayDateString(),
    category_id: existingTransaction.category_id || null,
    category_label: existingTransaction.category_label || null,
    customer_id: existingTransaction.customer_id || null,
    supplier_id: existingTransaction.supplier_id || null,
    payment_account_id: existingTransaction.payment_account_id || '',
    description: existingTransaction.description || '',
    tax_amount: existingTransaction.tax_amount || '',
  }
  includeTax.value = !!(existingTransaction.tax_amount && existingTransaction.tax_amount > 0)

  if (existingTransaction.receipt_image_data_url) {
    receiptPreviewUrl.value = existingTransaction.receipt_image_data_url
  }
}

async function loadDefaultPaymentAccount() {
  try {
    const response = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_default_payment_account',
    })
    form.value.payment_account_id = response || ''
  } catch {
    // Offline or unavailable — user can enter account manually
  }
}

// --- Event handlers ---

function onTypeChange(newType) {
  form.value.transaction_type = newType
  // Clear party selection on type switch to avoid cross-type data leaking
  form.value.customer_id = null
  form.value.supplier_id = null
}

function onCategorySelected(category) {
  form.value.category_id = category.name
  form.value.category_label = `${category.icon || ''} ${category.category_name}`.trim()
  showCategorySelector.value = false
}

async function onReceiptFileSelected(event) {
  const selectedFile = event.target.files?.[0]
  if (!selectedFile) return

  photoError.value = null
  try {
    const compressed = await compressFile(selectedFile)
    receiptPreviewUrl.value = compressed.dataUrl
    receiptBlob.value = compressed.blob
    receiptFilename.value = compressed.filename
  } catch (compressionError) {
    photoError.value = compressionError.message
  }
}

function clearReceiptPhoto() {
  receiptPreviewUrl.value = null
  receiptBlob.value = null
  receiptFilename.value = null
}

function close() {
  emit('close')
}

// --- Save ---

async function saveTransaction() {
  if (!form.value.amount || Number(form.value.amount) <= 0) {
    saveError.value = 'Please enter a valid amount'
    return
  }

  isSaving.value = true
  saveError.value = null

  try {
    const transactionData = {
      transaction_type: form.value.transaction_type,
      amount: Number(form.value.amount),
      date: form.value.date,
      category_id: form.value.category_id,
      category_label: form.value.category_label,
      customer_id: form.value.customer_id,
      supplier_id: form.value.supplier_id,
      payment_account_id: form.value.payment_account_id,
      description: form.value.description,
      tax_amount: includeTax.value ? Number(form.value.tax_amount || 0) : 0,
      receipt_image_blob: receiptBlob.value,
      receipt_image_name: receiptFilename.value,
      receipt_image_data_url: receiptPreviewUrl.value,
    }

    await transactionStore.addTransaction(transactionData)
    syncStore.syncAll() // Fire-and-forget — don't block UI on sync completion

    emit('saved')
    emit('close')
  } catch {
    saveError.value = 'Failed to save transaction. Please try again.'
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
