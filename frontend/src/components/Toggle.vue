<template>
  <button
    type="button"
    role="switch"
    :aria-checked="modelValue"
    class="relative h-5 w-9 rounded-full transition-colors"
    :style="{ backgroundColor: modelValue ? '#000000' : '#d1d5db' }"
    @click="emit('update:modelValue', !modelValue)"
  >
    <span
      class="absolute top-0.5 h-4 w-4 rounded-full shadow"
      :style="{
        backgroundColor: '#ffffff',
        left: modelValue ? '18px' : '2px',
        transition: 'left 0.15s ease',
      }"
    />
  </button>
</template>

<script setup>
defineProps({
  modelValue: { type: Boolean, required: true },
})

const emit = defineEmits(['update:modelValue'])
</script>
