<template>
  <div
    class="shrink-0 flex items-center justify-center rounded-xl"
    :class="[sizeClass, !color ? 'bg-surface-gray-2' : '']"
    :style="color ? { backgroundColor: color + '22' } : {}"
  >
    <span
      v-if="icon"
      class="text-ink-gray-8 [&>svg]:h-full [&>svg]:w-full"
      :class="iconSizeClass"
      v-html="iconSvg"
    />
    <span v-else class="text-base">📁</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getIconSvg } from '@/utils/icons'

const props = defineProps({
  icon: { type: String, default: null },
  color: { type: String, default: null },
  size: { type: String, default: 'md' }, // 'sm' | 'md' | 'lg'
})

const SIZE_CLASSES = {
  sm: 'h-8 w-8',
  md: 'h-10 w-10',
  lg: 'h-12 w-12',
}

const ICON_SIZE_CLASSES = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
}

const sizeClass = computed(() => SIZE_CLASSES[props.size] ?? SIZE_CLASSES.md)
const iconSizeClass = computed(() => ICON_SIZE_CLASSES[props.size] ?? ICON_SIZE_CLASSES.md)
const iconSvg = computed(() => (props.icon ? getIconSvg(props.icon) : ''))
</script>
