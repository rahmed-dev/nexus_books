<template>
  <BottomSheet
    :is-open="isOpen"
    :title="transaction ? 'Edit Transaction' : 'New Transaction'"
    max-height="92vh"
    @close="close"
  >
    <!-- Scrollable form body -->
    <div class="px-4 pb-6 pt-2">

      <!-- Transaction type tabs -->
      <SegmentedControl
        v-model="form.transaction_type"
        :options="TRANSACTION_TYPES"
        class="mb-5"
        @update:model-value="onTypeChange"
      />

      <!-- Amount -->
      <FormField label="Amount" class="mb-4">
        <input
          v-model="form.amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="0.00"
          inputmode="decimal"
          class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-3xl font-bold tracking-tight text-ink-gray-9 placeholder-ink-gray-3 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        />
      </FormField>

      <!-- Date -->
      <FormField label="Date" class="mb-4">
        <Input v-model="form.date" type="date" class="w-full" />
      </FormField>

      <!-- Nexus Account (From) -->
      <FormField label="Account" class="mb-4">
        <SelectTrigger
          placeholder="Select account…"
          :selected-item="selectedFromAccountItem"
          @click="showFromAccountSelector = true"
        />
      </FormField>

      <!-- To Account (Transfer only) -->
      <FormField v-if="form.transaction_type === 'Transfer'" label="To Account" class="mb-4">
        <SelectTrigger
          placeholder="Select destination account…"
          :selected-item="selectedToAccountItem"
          @click="showToAccountSelector = true"
        />
      </FormField>

      <!-- Category (hidden for Transfer) -->
      <FormField v-if="form.transaction_type !== 'Transfer'" label="Category" class="mb-4">
        <SelectTrigger
          placeholder="Select category…"
          :selected-item="selectedCategoryItem"
          @click="showCategorySelector = true"
        />
      </FormField>

      <!-- Party -->
      <FormField
        v-if="form.transaction_type !== 'Transfer'"
        :label="form.transaction_type === 'Income' ? 'Customer' : 'Supplier'"
        :optional="!selectedCategoryRequiresParty"
        class="mb-4"
      >
        <PartySelector
          v-model="activePartyId"
          :party-type="form.transaction_type === 'Income' ? 'Customer' : 'Supplier'"
        />
      </FormField>

      <!-- Description -->
      <FormField label="Description" :optional="true" class="mb-4">
        <textarea
          v-model="form.description"
          rows="2"
          placeholder="Add a note…"
          class="w-full resize-none rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        />
      </FormField>

      <!-- Tax toggle + amount -->
      <div class="mb-4">
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-ink-gray-6">Include tax</span>
          <Toggle v-model="includeTax" />
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
      <FormField label="Receipt photo" :optional="true" class="mb-6">
        <div v-if="receiptPreviewUrl" class="relative mb-2 inline-block">
          <img
            :src="receiptPreviewUrl"
            alt="Receipt preview"
            class="h-24 w-24 rounded-xl object-cover"
          />
          <button
            type="button"
            class="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-surface-gray-7 text-white"
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
      </FormField>

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
  </BottomSheet>

  <!-- CategorySelector has its own internal Teleport — rendered outside the sheet Teleport -->
  <CategorySelector
    v-if="showCategorySelector"
    :selected-category-id="form.category_id"
    :transaction-type="form.transaction_type"
    @select="onCategorySelected"
    @close="showCategorySelector = false"
  />

  <AccountSelectorSheet
    v-if="showFromAccountSelector"
    title="Select Account"
    :selected-account-name="form.nexus_account_id"
    @select="onFromAccountSelected"
    @close="showFromAccountSelector = false"
  />

  <AccountSelectorSheet
    v-if="showToAccountSelector"
    title="Select Destination Account"
    :selected-account-name="form.to_nexus_account_id"
    :exclude-account-name="form.nexus_account_id"
    @select="onToAccountSelected"
    @close="showToAccountSelector = false"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useTransactionStore } from '@/stores/transactions'
import { useSyncStore } from '@/stores/sync'
import { useCategoryStore } from '@/stores/categories'
import { useAccountStore } from '@/stores/accounts'
import BottomSheet from '@/components/BottomSheet.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import FormField from '@/components/FormField.vue'
import SelectTrigger from '@/components/SelectTrigger.vue'
import Toggle from '@/components/Toggle.vue'
import CategorySelector from '@/components/CategorySelector.vue'
import AccountSelectorSheet from '@/components/AccountSelectorSheet.vue'
import PartySelector from '@/components/PartySelector.vue'
import { usePhotoCompressor } from '@/composables/usePhotoCompressor'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  transaction: { type: Object, default: null }, // null = Add mode, Object = Edit mode
})

const emit = defineEmits(['close', 'saved'])

const transactionStore = useTransactionStore()
const syncStore = useSyncStore()
const categoryStore = useCategoryStore()
const accountStore = useAccountStore()
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
const showFromAccountSelector = ref(false)
const showToAccountSelector = ref(false)
const receiptPreviewUrl = ref(null)
const receiptBlob = ref(null)
const receiptFilename = ref(null)
const photoError = ref(null)
const isSaving = ref(false)
const saveError = ref(null)

// Resolved category object for SelectTrigger display
const selectedCategoryItem = computed(() => {
  if (!form.value.category_id) return null
  const category = categoryStore.categories.find((c) => c.name === form.value.category_id)
  return category
    ? { label: category.category_name, icon: category.icon, color: category.color }
    : { label: form.value.category_label, icon: null, color: null }
})

// Resolved from-account object for SelectTrigger display
const selectedFromAccountItem = computed(() => {
  if (!form.value.nexus_account_id) return null
  const account = accountStore.accounts.find((a) => a.name === form.value.nexus_account_id)
  return account ? { label: account.account_name, accountType: account.account_type } : null
})

// Resolved to-account object for SelectTrigger display
const selectedToAccountItem = computed(() => {
  if (!form.value.to_nexus_account_id) return null
  const account = accountStore.accounts.find((a) => a.name === form.value.to_nexus_account_id)
  return account ? { label: account.account_name, accountType: account.account_type } : null
})

// Whether the selected category requires a party (has an item set)
const selectedCategoryRequiresParty = computed(() => {
  if (!form.value.category_id) return false
  const category = categoryStore.categories.find((c) => c.name === form.value.category_id)
  return !!(category?.item)
})

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
    nexus_account_id: accountStore.defaultAccount?.name || null,
    to_nexus_account_id: null,
    description: '',
    tax_amount: '',
  }
}

function todayDateString() {
  return new Date().toISOString().split('T')[0]
}

function initializeForm() {
  resetFormState()
  if (props.transaction) {
    prefillFormForEdit(props.transaction)
  } else {
    // Pre-select default account if available
    form.value.nexus_account_id = accountStore.defaultAccount?.name || null
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
    nexus_account_id: existingTransaction.nexus_account || null,
    to_nexus_account_id: existingTransaction.to_nexus_account || null,
    description: existingTransaction.description || '',
    tax_amount: existingTransaction.tax_amount || '',
  }
  includeTax.value = !!(existingTransaction.tax_amount && existingTransaction.tax_amount > 0)

  if (existingTransaction.receipt_image_data_url) {
    receiptPreviewUrl.value = existingTransaction.receipt_image_data_url
  }
}

// --- Event handlers ---

function onTypeChange(newType) {
  form.value.transaction_type = newType
  // Clear party and transfer fields on type switch to avoid stale data
  form.value.customer_id = null
  form.value.supplier_id = null
  form.value.to_nexus_account_id = null
  if (newType === 'Transfer') {
    form.value.category_id = null
    form.value.category_label = null
  }
}

function onCategorySelected(category) {
  form.value.category_id = category.name
  form.value.category_label = category.category_name
  showCategorySelector.value = false
}

function onFromAccountSelected(account) {
  form.value.nexus_account_id = account.name
  // Clear to_account if it matches the newly selected from_account
  if (form.value.to_nexus_account_id === account.name) {
    form.value.to_nexus_account_id = null
  }
  showFromAccountSelector.value = false
}

function onToAccountSelected(account) {
  form.value.to_nexus_account_id = account.name
  showToAccountSelector.value = false
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

  // Party is mandatory when the selected category has an item set
  if (selectedCategoryRequiresParty.value) {
    const missingCustomer = form.value.transaction_type === 'Income' && !form.value.customer_id
    const missingSupplier = form.value.transaction_type === 'Expense' && !form.value.supplier_id
    if (missingCustomer || missingSupplier) {
      saveError.value = `${form.value.transaction_type === 'Income' ? 'Customer' : 'Supplier'} is required for this category`
      return
    }
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
      nexus_account: form.value.nexus_account_id,
      to_nexus_account: form.value.to_nexus_account_id,
      description: form.value.description,
      tax_amount: includeTax.value ? Number(form.value.tax_amount || 0) : 0,
      receipt_image_blob: receiptBlob.value,
      receipt_image_name: receiptFilename.value,
      receipt_image_data_url: receiptPreviewUrl.value,
    }

    if (props.transaction?.name) {
      // Edit mode — synced Frappe transaction: cancel + amend
      await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.amend_transaction',
        params: {
          name: props.transaction.name,
          data: JSON.stringify({
            transaction_type: transactionData.transaction_type,
            amount: transactionData.amount,
            date: transactionData.date,
            category: transactionData.category_id,
            customer: transactionData.customer_id,
            supplier: transactionData.supplier_id,
            nexus_account: transactionData.nexus_account,
            to_nexus_account: transactionData.to_nexus_account,
            description: transactionData.description,
            tax_amount: transactionData.tax_amount,
          }),
        },
      })
    } else if (props.transaction?.id) {
      // Edit mode — IDB pending transaction: update in place + re-queue
      await transactionStore.updateIdbTransaction(props.transaction.id, transactionData)
      syncStore.syncAll()
    } else {
      // Add mode — new transaction: await sync so it's immediately visible in TransactionList
      await transactionStore.addTransaction(transactionData)
      await syncStore.syncAll()
    }

    emit('saved')
    emit('close')
  } catch {
    saveError.value = 'Failed to save transaction. Please try again.'
  } finally {
    isSaving.value = false
  }
}
</script>
