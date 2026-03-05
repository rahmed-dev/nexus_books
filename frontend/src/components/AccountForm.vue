<template>
  <BottomSheet
    :is-open="isOpen"
    :title="account ? 'Edit Account' : 'New Account'"
    @close="emit('close')"
  >
    <div class="px-4 pb-4 pt-2 space-y-4">

      <!-- Account name -->
      <FormField label="Account Name">
        <input
          v-model="form.account_name"
          type="text"
          placeholder="e.g. Main Wallet"
          class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2.5 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        />
      </FormField>

      <!-- Account type -->
      <FormField label="Type">
        <SegmentedControl
          v-model="form.account_type"
          :options="ACCOUNT_TYPES"
        />
      </FormField>

      <!-- Default toggle -->
      <div class="flex items-center justify-between py-1">
        <span class="text-sm font-medium text-ink-gray-7">Use as default account</span>
        <Toggle v-model="form.is_default" />
      </div>

      <p class="text-xs text-ink-gray-4">
        To link this account to an ERPNext GL account, open it from Desk.
      </p>

    </div>

    <template #footer>
      <div class="px-4 py-3">
        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white transition-opacity active:opacity-80 disabled:opacity-40"
          :disabled="isSaving || !form.account_name.trim()"
          @click="save"
        >
          {{ isSaving ? 'Saving…' : (account ? 'Save Changes' : 'Create Account') }}
        </button>
        <p v-if="saveError" class="mt-2 text-center text-xs text-red-500">{{ saveError }}</p>
      </div>
    </template>
  </BottomSheet>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import BottomSheet from '@/components/BottomSheet.vue'
import FormField from '@/components/FormField.vue'
import SegmentedControl from '@/components/SegmentedControl.vue'
import Toggle from '@/components/Toggle.vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  account: { type: Object, default: null },
})

const emit = defineEmits(['close', 'saved'])

const accountStore = useAccountStore()

const ACCOUNT_TYPES = [
  { value: 'Bank', label: 'Bank' },
  { value: 'Cash', label: 'Cash' },
]

const form = ref(buildEmptyForm())
const isSaving = ref(false)
const saveError = ref(null)

function buildEmptyForm() {
  return { account_name: '', account_type: 'Cash', is_default: false }
}

watch(
  () => props.isOpen,
  (isNowOpen) => {
    if (isNowOpen) {
      saveError.value = null
      if (props.account) {
        form.value = {
          account_name: props.account.account_name || '',
          account_type: props.account.account_type || 'Cash',
          is_default: !!props.account.is_default,
        }
      } else {
        form.value = buildEmptyForm()
      }
    }
  },
)

async function save() {
  if (!form.value.account_name.trim()) return
  isSaving.value = true
  saveError.value = null
  try {
    if (props.account) {
      await accountStore.updateAccount(
        props.account.name,
        form.value.account_name,
        form.value.account_type,
        form.value.is_default,
      )
    } else {
      await accountStore.createAccount(
        form.value.account_name,
        form.value.account_type,
        form.value.is_default,
      )
    }
    emit('saved')
    emit('close')
  } catch {
    saveError.value = 'Failed to save account. Please try again.'
  } finally {
    isSaving.value = false
  }
}
</script>
