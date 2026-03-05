<template>
  <button
    type="button"
    class="flex flex-col items-center gap-1.5 rounded-xl p-3 text-center transition-transform active:scale-95"
    :class="[selected ? 'ring-2 ring-ink-gray-9' : '', !color ? 'bg-surface-gray-2' : '']"
    :style="color ? { backgroundColor: color + '22' } : {}"
    @click="emit('click')"
  >
    <span
      v-if="icon"
      class="h-8 w-8 text-ink-gray-8 [&>svg]:h-full [&>svg]:w-full"
      v-html="iconSvg"
    />
    <span v-else class="flex h-8 w-8 items-center justify-center text-2xl">💰</span>
    <span class="text-xs font-medium leading-tight text-ink-gray-7">{{ label }}</span>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { getIconSvg } from '@/utils/icons'

const props = defineProps({
  label: { type: String, required: true },
  icon: { type: String, default: null },
  color: { type: String, default: null },
  categoryType: { type: String, default: null },
  selected: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])

const iconSvg = computed(() => (props.icon ? getIconSvg(props.icon) : ''))
</script>
