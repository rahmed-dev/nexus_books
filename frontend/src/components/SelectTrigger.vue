<template>
  <button
    type="button"
    class="flex w-full items-center justify-between rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-4 py-3 text-sm active:bg-surface-gray-2"
    @click="emit('click')"
  >
    <!-- Selected state: avatar + label -->
    <span v-if="selectedItem" class="flex items-center gap-2.5 min-w-0">
      <AccountAvatar v-if="selectedItem.accountType" :account-type="selectedItem.accountType" size="sm" />
      <CategoryAvatar v-else :icon="selectedItem.icon" :color="selectedItem.color" size="sm" />
      <span class="truncate text-ink-gray-9">{{ selectedItem.label }}</span>
    </span>

    <!-- Empty state: placeholder -->
    <span v-else class="text-ink-gray-4">{{ placeholder }}</span>

    <!-- Chevron -->
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="ml-2 h-4 w-4 shrink-0 text-ink-gray-4"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  </button>
</template>

<script setup>
import CategoryAvatar from '@/components/CategoryAvatar.vue'
import AccountAvatar from '@/components/AccountAvatar.vue'

defineProps({
  placeholder: { type: String, default: 'Select…' },
  // selectedItem: { label, icon, color } | { label, accountType } | null
  selectedItem: { type: Object, default: null },
})

const emit = defineEmits(['click'])
</script>
