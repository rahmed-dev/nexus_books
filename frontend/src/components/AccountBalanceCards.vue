<template>
  <div>
    <!-- Loading skeleton -->
    <div v-if="loading" class="flex gap-3 overflow-x-auto pb-1">
      <div
        v-for="n in 3"
        :key="n"
        class="h-20 w-36 flex-shrink-0 animate-pulse rounded-xl bg-surface-gray-2"
      ></div>
    </div>

    <!-- Account cards -->
    <div v-else class="flex gap-3 overflow-x-auto pb-1">
      <div
        v-for="account in accounts"
        :key="account.name"
        class="flex w-40 flex-shrink-0 flex-col gap-2 rounded-xl border border-surface-gray-2 bg-surface-white p-3 shadow-sm"
      >
        <!-- Avatar + type label -->
        <div class="flex items-center gap-2">
          <AccountAvatar :account-type="account.account_type" size="sm" />
          <span class="text-xs text-ink-gray-4">{{ account.account_type }}</span>
          <span v-if="account.is_default" class="ml-auto text-xs text-ink-gray-3">●</span>
        </div>

        <!-- Account name -->
        <p class="truncate text-xs font-medium text-ink-gray-7">{{ account.account_name }}</p>

        <!-- Balance -->
        <p class="text-sm font-semibold" :class="account.balance >= 0 ? 'text-ink-gray-9' : 'text-red-500'">
          {{ formatCurrency(account.balance, currencySymbol) }}
        </p>
      </div>

      <p v-if="!accounts.length" class="text-sm text-ink-gray-4">
        No accounts found. Add one in Settings.
      </p>
    </div>
  </div>
</template>

<script setup>
import { formatCurrency } from '@/utils/currency'
import AccountAvatar from '@/components/AccountAvatar.vue'

defineProps({
  accounts:       { type: Array,  default: () => [] },
  currencySymbol: { type: String, default: 'Rs.' },
  loading:        { type: Boolean, default: false },
})
</script>
