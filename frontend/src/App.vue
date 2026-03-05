<template>
  <FrappeUIProvider>
    <AppShell>
      <router-view />

      <template #bottom-nav>
        <!-- Overview tab -->
        <router-link
          to="/dashboard"
          class="flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium transition-colors"
          :class="$route.name === 'Dashboard' ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Overview
        </router-link>

        <!-- Transactions tab -->
        <router-link
          to="/transactions"
          class="flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium transition-colors"
          :class="$route.name === 'Transactions' ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Transactions
        </router-link>

        <!-- Settings tab -->
        <router-link
          to="/settings"
          class="relative flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium transition-colors"
          :class="$route.name === 'Settings' ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          Settings
          <!-- Sync status dot badge -->
          <span v-if="syncBadgeVisible" class="absolute right-4 top-2 h-2 w-2 rounded-full" :class="syncBadgeDotClass" />
        </router-link>
      </template>
    </AppShell>
  </FrappeUIProvider>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { FrappeUIProvider } from 'frappe-ui'
import { useRoute } from 'vue-router'
import AppShell from '@/components/AppShell.vue'
import { useSyncStore } from '@/stores/sync'
import { useAccountStore } from '@/stores/accounts'
import { useItemStore } from '@/stores/items'
import { useSettingsStore } from '@/stores/settings'

const syncStore = useSyncStore()
const accountStore = useAccountStore()
const itemStore = useItemStore()
const settingsStore = useSettingsStore()
const $route = useRoute()

// Sync dot badge on Settings tab — visible when not idle+online
const syncBadgeVisible = computed(() =>
  !syncStore.isOnline || syncStore.syncStatus === 'syncing' || syncStore.syncStatus === 'failed',
)

const syncBadgeDotClass = computed(() => {
  if (!syncStore.isOnline) return 'bg-gray-400'
  if (syncStore.syncStatus === 'syncing') return 'bg-yellow-400'
  if (syncStore.syncStatus === 'failed') return 'bg-red-500'
  return ''
})

onMounted(() => {
  syncStore.setupOnlineOfflineListeners()
  syncStore.startPeriodicSync()
  settingsStore.loadSettings()
  accountStore.loadAccounts()
  itemStore.loadItems()
})
</script>
