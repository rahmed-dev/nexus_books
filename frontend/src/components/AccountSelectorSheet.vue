<template>
  <BottomSheet
    :is-open="true"
    :title="title"
    @close="emit('close')"
  >
    <div class="pb-4">
      <button
        v-for="account in selectableAccounts"
        :key="account.name"
        type="button"
        class="flex w-full items-center justify-between border-b border-outline-gray-1 px-4 py-3.5 active:bg-surface-gray-1"
        @click="emit('select', account)"
      >
        <div class="flex items-center gap-3">
          <AccountAvatar :account-type="account.account_type" size="sm" />
          <div class="text-left">
            <p class="text-sm font-medium text-ink-gray-9">{{ account.account_name }}</p>
            <p class="text-xs text-ink-gray-5">{{ account.account_type }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <p class="text-sm font-medium text-ink-gray-7">{{ formatBalance(account.balance) }}</p>
          <span
            v-if="account.is_default"
            class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-xs text-ink-gray-5"
          >
            Default
          </span>
          <svg
            v-if="selectedAccountName === account.name"
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 text-ink-gray-9"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2.5"
          >
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      </button>

      <EmptyState
        v-if="selectableAccounts.length === 0"
        title="No accounts available"
        subtitle="Add an account from Settings → Accounts"
        class="py-8"
      />
    </div>
  </BottomSheet>
</template>

<script setup>
import { computed } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import BottomSheet from '@/components/BottomSheet.vue'
import EmptyState from '@/components/EmptyState.vue'
import AccountAvatar from '@/components/AccountAvatar.vue'

const props = defineProps({
  title: { type: String, default: 'Select Account' },
  selectedAccountName: { type: String, default: null },
  excludeAccountName: { type: String, default: null },
})

const emit = defineEmits(['select', 'close'])

const accountStore = useAccountStore()

function formatBalance(amount) {
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(amount || 0)
}

const selectableAccounts = computed(() =>
  accountStore.accounts.filter((a) => a.name !== props.excludeAccountName),
)
</script>
