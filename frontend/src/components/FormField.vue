<template>
  <div>
    <label class="mb-1.5 block text-xs font-medium text-ink-gray-6">
      {{ label }}
      <span v-if="optional" class="font-normal text-ink-gray-4">(optional)</span>
    </label>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  optional: { type: Boolean, default: false },
})
</script>
