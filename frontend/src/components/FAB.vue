<template>
  <!--
    Floating Action Button — fixed above the bottom nav bar.
    Emits 'click' for the parent to handle (e.g. open AddTransactionForm sheet).
    bottom offset = bottom-nav height (~56px) + safe area + 16px gap
  -->
  <button
    type="button"
    class="fixed right-4 flex h-14 w-14 items-center justify-center rounded-full bg-ink-gray-9 shadow-lg active:scale-95"
    :style="{ bottom: 'calc(56px + env(safe-area-inset-bottom) + 1rem)' }"
    :aria-label="label"
    @click="emit('click')"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="h-6 w-6 text-surface-white"
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      stroke-width="2.5"
    >
      <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
    </svg>
  </button>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    default: 'Add transaction',
  },
})

const emit = defineEmits(['click'])
</script>
