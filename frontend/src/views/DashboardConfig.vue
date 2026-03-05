<template>
  <div class="flex flex-col pb-20">
    <PageHeader title="Dashboard" back-to="/settings" />

    <p class="px-4 pb-3 text-sm text-ink-gray-5">
      Toggle widgets on or off and drag to reorder.
    </p>

    <!-- Sortable widget list -->
    <div ref="listRef" class="border-t border-outline-gray-1">
      <div
        v-for="item in localConfig"
        :key="item.id"
        class="flex items-center gap-3 border-b border-outline-gray-1 bg-surface-white px-4 py-3"
      >
        <!-- Drag handle -->
        <span class="drag-handle cursor-grab touch-none text-ink-gray-3 active:cursor-grabbing">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 8h16M4 16h16" />
          </svg>
        </span>

        <!-- Widget icon -->
        <span
          class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-surface-gray-1 text-ink-gray-6 [&>svg]:h-4 [&>svg]:w-4"
          v-html="getIconSvg(widgetMeta(item.id).icon)"
        />

        <!-- Label + description -->
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-ink-gray-9">{{ widgetMeta(item.id).label }}</p>
          <p class="truncate text-xs text-ink-gray-4">{{ widgetMeta(item.id).description }}</p>
        </div>

        <!-- Toggle -->
        <Toggle :model-value="item.enabled" @update:model-value="(val) => toggleWidget(item.id, val)" />
      </div>
    </div>

    <p class="px-4 pt-3 text-center text-xs text-ink-gray-3">
      Changes are saved automatically.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sortable from 'sortablejs'
import { useDashboardStore } from '@/stores/dashboard'
import { DASHBOARD_WIDGETS } from '@/data/dashboard-widgets'
import { getIconSvg } from '@/utils/icons'
import PageHeader from '@/components/PageHeader.vue'
import Toggle from '@/components/Toggle.vue'

const dashboardStore = useDashboardStore()

// Local copy — mutated by drag/drop and toggles, synced to store on each change
const localConfig = ref([...dashboardStore.config])

const listRef = ref(null)

const WIDGET_META = Object.fromEntries(DASHBOARD_WIDGETS.map((w) => [w.id, w]))

function widgetMeta(id) {
  return WIDGET_META[id] ?? { label: id, icon: 'layout-dashboard', description: '' }
}

function toggleWidget(id, enabled) {
  localConfig.value = localConfig.value.map((w) => (w.id === id ? { ...w, enabled } : w))
  dashboardStore.saveConfig(localConfig.value)
}

onMounted(() => {
  if (!listRef.value) return

  Sortable.create(listRef.value, {
    handle: '.drag-handle',
    animation: 150,
    ghostClass: 'opacity-40',
    onEnd({ oldIndex, newIndex }) {
      if (oldIndex === newIndex) return
      const updated = [...localConfig.value]
      const [moved] = updated.splice(oldIndex, 1)
      updated.splice(newIndex, 0, moved)
      localConfig.value = updated
      dashboardStore.saveConfig(updated)
    },
  })
})
</script>
