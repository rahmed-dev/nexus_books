<template>
  <div class="flex flex-col pb-20">

    <PageHeader title="Settings" />

    <!-- Sync status -->
    <div class="mx-4 mb-4 flex items-center gap-2 rounded-xl bg-surface-gray-1 px-4 py-3">
      <span class="inline-block h-2 w-2 rounded-full shrink-0" :class="syncDotClass" />
      <span class="text-sm text-ink-gray-7">{{ syncStatusLabel }}</span>
      <button
        v-if="syncStore.isOnline"
        type="button"
        class="ml-auto text-xs font-medium text-ink-gray-5 active:text-ink-gray-9"
        @click="syncStore.syncAll()"
      >
        Sync now
      </button>
    </div>

    <!-- Masters section -->
    <section class="mb-6">
      <p class="px-4 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        Masters
      </p>
      <div class="border-t border-outline-gray-1">
        <!-- Accounts -->
        <router-link
          to="/accounts"
          class="flex items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
              </svg>
            </div>
            <div>
              <span class="text-sm font-medium text-ink-gray-9">Accounts</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="accountStore.accounts.length > 0" class="text-xs text-ink-gray-5">
              {{ accountStore.accounts.length }}
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </router-link>
        <!-- Categories -->
        <router-link
          to="/categories"
          class="flex items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              </svg>
            </div>
            <span class="text-sm font-medium text-ink-gray-9">Categories</span>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
      </div>
    </section>

    <!-- App Settings section -->
    <section class="mb-6">
      <p class="px-4 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        App Settings
      </p>
      <div class="border-t border-outline-gray-1">
        <!-- Dashboard -->
        <router-link
          to="/settings/dashboard"
          class="flex items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-ink-gray-9">Dashboard</p>
              <p class="text-xs text-ink-gray-5">Reorder and toggle widgets</p>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </router-link>
        <a
          href="/app/nexus-books-settings"
          target="_blank"
          class="flex items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-ink-gray-9">Nexus Books Settings</p>
              <p class="text-xs text-ink-gray-5">Default account, sync options</p>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>
      </div>
    </section>

    <!-- ERPNext Integration section -->
    <section class="mb-6">
      <p class="px-4 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        ERPNext Integration
      </p>
      <div class="border-t border-outline-gray-1">
        <!-- Pull from ERPNext -->
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1 disabled:opacity-40"
          :disabled="!hasLinkedAccounts"
          :title="!hasLinkedAccounts ? 'No accounts linked to ERPNext' : ''"
          @click="showReconcileSheet = true"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-ink-gray-9 text-left">Pull from ERPNext</p>
              <p class="text-xs text-ink-gray-5 text-left">Import month-end accountant entries</p>
            </div>
          </div>
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        <!-- Sync Errors -->
        <button
          type="button"
          class="flex w-full items-center justify-between px-4 py-4 active:bg-surface-gray-1 border-b border-outline-gray-1"
          @click="showSyncErrorsSheet = true"
        >
          <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-surface-gray-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p class="text-sm font-medium text-ink-gray-9 text-left">Sync Errors</p>
              <p class="text-xs text-ink-gray-5 text-left">Transactions that failed to post to ERPNext</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span
              v-if="failedGlCount > 0"
              class="flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 text-xs font-bold text-white"
            >
              {{ failedGlCount }}
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-ink-gray-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>
      </div>
    </section>

    <SyncErrorsSheet
      v-if="showSyncErrorsSheet"
      @close="showSyncErrorsSheet = false"
      @count-changed="failedGlCount = $event"
    />

    <ReconcileSheet
      v-if="showReconcileSheet"
      @close="showReconcileSheet = false"
    />

    <!-- About section -->
    <section>
      <p class="px-4 pb-1 pt-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">
        About
      </p>
      <div class="border-t border-b border-outline-gray-1">
        <div class="flex items-center justify-between px-4 py-4">
          <span class="text-sm text-ink-gray-6">Version</span>
          <span class="text-sm font-medium text-ink-gray-9">1.1.2</span>
        </div>
        <div class="flex items-center justify-between border-t border-outline-gray-1 px-4 py-4">
          <span class="text-sm text-ink-gray-6">Logged in as</span>
          <span class="text-sm font-medium text-ink-gray-9">{{ currentUser }}</span>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useSyncStore } from '@/stores/sync'
import { useAccountStore } from '@/stores/accounts'
import PageHeader from '@/components/PageHeader.vue'
import SyncErrorsSheet from '@/components/SyncErrorsSheet.vue'
import ReconcileSheet from '@/components/ReconcileSheet.vue'

const syncStore = useSyncStore()
const accountStore = useAccountStore()

const showSyncErrorsSheet = ref(false)
const showReconcileSheet = ref(false)
const failedGlCount = ref(0)

const hasLinkedAccounts = computed(() =>
  accountStore.accounts.some((a) => a.linked_account),
)

const currentUser = window.user_id || 'Unknown'

onMounted(async () => {
  try {
    const failed = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_failed_gl_transactions',
      params: { limit: 50 },
    })
    failedGlCount.value = (failed || []).length
  } catch {
    // Not critical — badge just won't show
  }
})

const syncDotClass = computed(() => {
  if (!syncStore.isOnline) return 'bg-gray-400'
  if (syncStore.syncStatus === 'syncing') return 'bg-yellow-400'
  if (syncStore.syncStatus === 'failed') return 'bg-red-500'
  if (syncStore.syncStatus === 'success') return 'bg-green-500'
  return 'bg-green-500' // idle + online = connected
})

const syncStatusLabel = computed(() => {
  if (!syncStore.isOnline) return 'Offline — changes saved locally'
  if (syncStore.syncStatus === 'syncing') return 'Syncing with ERPNext…'
  if (syncStore.syncStatus === 'failed') return 'Sync failed — tap to retry'
  if (syncStore.syncStatus === 'success') return 'All synced'
  return 'Connected to ERPNext'
})
</script>
