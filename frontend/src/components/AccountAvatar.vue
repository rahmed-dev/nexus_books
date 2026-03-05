<template>
  <div
    class="flex shrink-0 items-center justify-center rounded-xl"
    :class="[sizeClass, bgClass]"
  >
    <span
      class="[&>svg]:h-full [&>svg]:w-full"
      :class="[iconSizeClass, iconColorClass]"
      v-html="iconSvg"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { getIconSvg } from '@/utils/icons'

const props = defineProps({
  accountType: { type: String, default: 'Bank' }, // 'Bank' | 'Cash'
  size:        { type: String, default: 'md' },   // 'sm' | 'md' | 'lg'
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

const isBank = computed(() => props.accountType === 'Bank')

const sizeClass     = computed(() => SIZE_CLASSES[props.size]      ?? SIZE_CLASSES.md)
const iconSizeClass = computed(() => ICON_SIZE_CLASSES[props.size] ?? ICON_SIZE_CLASSES.md)
const bgClass       = computed(() => isBank.value ? 'bg-blue-50'   : 'bg-amber-50')
const iconColorClass= computed(() => isBank.value ? 'text-blue-500' : 'text-amber-500')
const iconSvg       = computed(() => getIconSvg(isBank.value ? 'landmark' : 'wallet'))
</script>
