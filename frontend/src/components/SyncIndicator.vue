<template>
  <div v-if="visible" class="flex items-center gap-1.5 px-3 py-1.5">
    <span
      class="inline-block h-1.5 w-1.5 rounded-full"
      :class="dotColorClass"
    />
    <span class="text-xs font-medium" :class="textColorClass">
      {{ statusLabel }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useSyncStore } from '@/stores/sync'

const syncStore = useSyncStore()

const STATUS_CONFIG = {
  syncing: {
    label: 'Syncing…',
    dotColor: 'bg-yellow-400',
    textColor: 'text-yellow-700',
  },
  success: {
    label: 'Synced',
    dotColor: 'bg-green-500',
    textColor: 'text-green-700',
  },
  failed: {
    label: 'Sync failed',
    dotColor: 'bg-red-500',
    textColor: 'text-red-700',
  },
  offline: {
    label: 'Offline',
    dotColor: 'bg-gray-400',
    textColor: 'text-ink-gray-5',
  },
  idle: null, // hidden when idle + online
}

const currentStatus = computed(() => {
  if (!syncStore.isOnline) return 'offline'
  return syncStore.syncStatus // 'idle' | 'syncing' | 'success' | 'failed'
})

const config = computed(() => STATUS_CONFIG[currentStatus.value])

const visible = computed(() => config.value !== null)
const statusLabel = computed(() => config.value?.label ?? '')
const dotColorClass = computed(() => config.value?.dotColor ?? '')
const textColorClass = computed(() => config.value?.textColor ?? '')
</script>
