<template>
  <div class="py-16 text-center">
    <p class="text-sm font-medium text-ink-gray-7">{{ title }}</p>
    <p v-if="subtitle" class="mt-1 text-xs text-ink-gray-5">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: null },
})
</script>
