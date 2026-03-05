<template>
  <span
    v-if="config"
    class="rounded-full px-1.5 py-0.5 text-xs font-medium"
    :class="config.classes"
  >
    {{ config.label }}
  </span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, default: null },
})

const BADGE_CONFIG = {
  pending: { label: 'Pending', classes: 'bg-yellow-100 text-yellow-800' },
  syncing: { label: 'Syncing…', classes: 'bg-blue-100 text-blue-800' },
  failed:  { label: 'Failed',   classes: 'bg-red-100 text-red-800' },
}

const config = computed(() => BADGE_CONFIG[props.status] ?? null)
</script>
