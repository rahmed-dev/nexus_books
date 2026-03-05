<template>
  <button
    type="button"
    class="shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors"
    :class="active
      ? 'bg-surface-gray-7 text-white'
      : 'bg-surface-gray-2 text-ink-gray-6'"
  >
    <slot />
  </button>
</template>

<script setup>
defineProps({
  active: { type: Boolean, default: false },
})
</script>
