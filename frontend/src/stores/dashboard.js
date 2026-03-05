import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { DASHBOARD_WIDGETS, DEFAULT_CONFIG } from '@/data/dashboard-widgets'

const STORAGE_KEY = 'nexus_dashboard_config'

export const useDashboardStore = defineStore('dashboard', () => {
  const config = ref([...DEFAULT_CONFIG])

  function loadConfig() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return

      const saved = JSON.parse(raw)

      // Keep saved order and enabled state, append any new widgets added since last save
      const savedIds = new Set(saved.map((w) => w.id))
      const knownIds = new Set(DASHBOARD_WIDGETS.map((w) => w.id))

      const merged = [
        ...saved.filter((w) => knownIds.has(w.id)),          // known saved entries
        ...DEFAULT_CONFIG.filter((w) => !savedIds.has(w.id)), // new widgets not yet saved
      ]

      config.value = merged
    } catch {
      config.value = [...DEFAULT_CONFIG]
    }
  }

  function saveConfig(newConfig) {
    config.value = [...newConfig]
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config.value))
  }

  function setWidgetEnabled(id, enabled) {
    const updated = config.value.map((w) => (w.id === id ? { ...w, enabled } : w))
    saveConfig(updated)
  }

  const orderedEnabledWidgetIds = computed(() =>
    config.value.filter((w) => w.enabled).map((w) => w.id),
  )

  return { config, loadConfig, saveConfig, setWidgetEnabled, orderedEnabledWidgetIds }
})
