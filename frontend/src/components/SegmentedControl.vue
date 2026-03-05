<template>
  <div class="grid gap-1 rounded-xl bg-surface-gray-1 p-1" :style="{ gridTemplateColumns: `repeat(${options.length}, 1fr)` }">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="rounded-lg py-2 text-sm font-medium transition-colors"
      :class="
        modelValue === option.value
          ? 'bg-surface-white text-ink-gray-9 shadow-sm'
          : 'text-ink-gray-5'
      "
      @click="emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, required: true },
  options: { type: Array, required: true }, // [{ value: String, label: String }]
})

const emit = defineEmits(['update:modelValue'])
</script>
