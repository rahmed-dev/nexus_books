<template>
  <div class="flex flex-col pb-20">

    <PageHeader title="Accounts" back-to="/settings" />

    <EmptyState
      v-if="!accountStore.isLoading && accountStore.accounts.length === 0"
      title="No accounts yet"
      subtitle="Add your first account to get started"
      class="mt-12"
    />

    <div v-else class="border-t border-outline-gray-1">
      <button
        v-for="account in accountStore.accounts"
        :key="account.name"
        type="button"
        class="flex w-full items-center justify-between border-b border-outline-gray-1 px-4 py-4 active:bg-surface-gray-1"
        @click="openEditForm(account)"
      >
        <div class="flex items-center gap-3">
          <AccountAvatar :account-type="account.account_type" size="md" />
          <div class="text-left">
            <p class="text-sm font-medium text-ink-gray-9">{{ account.account_name }}</p>
            <p class="text-xs text-ink-gray-5">{{ account.account_type }}</p>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div class="text-right">
            <p class="text-sm font-semibold text-ink-gray-9">
              {{ formatCurrency(account.balance, settingsStore.currencySymbol) }}
            </p>
            <p class="text-xs" :class="account.balance_source === 'erpnext' ? 'text-green-600' : 'text-ink-gray-4'">
              {{ account.balance_source === 'erpnext' ? 'GL' : 'Nexus' }}
            </p>
          </div>
          <span
            v-if="account.is_default"
            class="rounded-full bg-surface-gray-7 px-2 py-0.5 text-xs font-medium text-white"
          >
            Default
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </button>
    </div>

    <FAB @click="openCreateForm" />

    <AccountForm
      :is-open="showAccountForm"
      :account="selectedAccount"
      @close="closeForm"
      @saved="closeForm"
    />

  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAccountStore } from '@/stores/accounts'
import { useSettingsStore } from '@/stores/settings'
import { formatCurrency } from '@/utils/currency'
import PageHeader from '@/components/PageHeader.vue'
import EmptyState from '@/components/EmptyState.vue'
import FAB from '@/components/FAB.vue'
import AccountForm from '@/components/AccountForm.vue'
import AccountAvatar from '@/components/AccountAvatar.vue'

const accountStore = useAccountStore()
const settingsStore = useSettingsStore()

const showAccountForm = ref(false)
const selectedAccount = ref(null)

function openCreateForm() {
  selectedAccount.value = null
  showAccountForm.value = true
}

function openEditForm(account) {
  selectedAccount.value = account
  showAccountForm.value = true
}

function closeForm() {
  showAccountForm.value = false
  selectedAccount.value = null
}
</script>
