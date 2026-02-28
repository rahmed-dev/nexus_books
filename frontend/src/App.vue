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

        <!-- Categories tab -->
        <router-link
          to="/categories"
          class="flex flex-1 flex-col items-center gap-1 py-2 text-xs font-medium transition-colors"
          :class="$route.name === 'Categories' ? 'text-ink-gray-9' : 'text-ink-gray-4'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
          </svg>
          Categories
        </router-link>

        <SyncIndicator />
      </template>
    </AppShell>
  </FrappeUIProvider>
</template>

<script setup>
import { onMounted } from 'vue'
import { FrappeUIProvider } from 'frappe-ui'
import { useRoute } from 'vue-router'
import AppShell from '@/components/AppShell.vue'
import SyncIndicator from '@/components/SyncIndicator.vue'
import { useSyncStore } from '@/stores/sync'

const syncStore = useSyncStore()
const $route = useRoute()

onMounted(() => {
  syncStore.setupOnlineOfflineListeners()
  syncStore.startPeriodicSync()
})
</script>
