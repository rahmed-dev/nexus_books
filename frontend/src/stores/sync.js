import { defineStore } from 'pinia'
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { useTransactionStore } from './transactions'

const BACKGROUND_SYNC_TAG = 'sync-transactions'
const MAX_RETRY_ATTEMPTS = 3
const PERIODIC_SYNC_INTERVAL_MS = 5 * 60 * 1000 // 5 minutes

export const useSyncStore = defineStore('sync', () => {
  const isOnline = ref(navigator.onLine)
  const isSyncing = ref(false)
  const syncStatus = ref('idle') // 'idle' | 'syncing' | 'success' | 'failed'
  const lastSyncAt = ref(null)

  // Track in-flight transaction IDs to prevent duplicate syncs
  const syncInProgressIds = new Set()

  // --- Lifecycle setup (call once from App.vue onMounted) ---

  function setupOnlineOfflineListeners() {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
  }

  function handleOnline() {
    isOnline.value = true
    syncAll()
  }

  function handleOffline() {
    isOnline.value = false
    syncStatus.value = 'idle'
  }

  // --- Background sync registration ---

  async function registerBackgroundSync() {
    const supportsBackgroundSync =
      'serviceWorker' in navigator &&
      'sync' in (window.ServiceWorkerRegistration?.prototype ?? {})

    if (supportsBackgroundSync) {
      try {
        const swRegistration = await navigator.serviceWorker.ready
        await swRegistration.sync.register(BACKGROUND_SYNC_TAG)
      } catch {
        // Background Sync API unavailable — fall back to foreground sync
        await syncAll()
      }
    } else {
      await syncAll()
    }
  }

  // --- Sync orchestration ---

  async function syncAll() {
    if (isSyncing.value || !isOnline.value) return

    isSyncing.value = true
    syncStatus.value = 'syncing'

    try {
      const transactionStore = useTransactionStore()
      const pendingTransactions = await transactionStore.getPendingTransactions()

      for (const pendingTransaction of pendingTransactions) {
        if (syncInProgressIds.has(pendingTransaction.id)) continue
        await syncOneTransaction(pendingTransaction)
      }

      syncStatus.value = 'success'
      lastSyncAt.value = new Date().toISOString()
    } catch {
      syncStatus.value = 'failed'
    } finally {
      isSyncing.value = false
    }
  }

  async function syncOneTransaction(pendingTransaction) {
    syncInProgressIds.add(pendingTransaction.id)
    const transactionStore = useTransactionStore()

    try {
      await transactionStore.markTransactionSyncing(pendingTransaction.id)

      let receiptImageUrl = null
      if (pendingTransaction.receipt_image_blob) {
        receiptImageUrl = await uploadReceiptPhoto(
          pendingTransaction.receipt_image_blob,
          pendingTransaction.receipt_image_name,
        )
      }

      const payload = {
        transaction_type: pendingTransaction.transaction_type,
        date: pendingTransaction.date,
        category: pendingTransaction.category_id,
        amount: pendingTransaction.amount,
        customer: pendingTransaction.customer_id || null,
        supplier: pendingTransaction.supplier_id || null,
        payment_account: pendingTransaction.payment_account_id,
        tax_amount: pendingTransaction.tax_amount || 0,
        description: pendingTransaction.description || '',
        receipt_image: receiptImageUrl,
        tags: pendingTransaction.tags || '',
      }

      const response = await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.sync_engine.sync_transaction_to_erpnext',
        params: { transaction_data: payload },
      })

      if (response?.status === 'success') {
        await transactionStore.markTransactionSynced(
          pendingTransaction.id,
          response.reference_doctype,
          response.reference_name,
        )
      } else {
        throw new Error(response?.error || 'Sync returned no success status')
      }
    } catch (syncError) {
      const retriesUsed = pendingTransaction.retry_count || 0
      await transactionStore.markTransactionFailed(
        pendingTransaction.id,
        syncError.message,
        retriesUsed,
      )

      if (retriesUsed < MAX_RETRY_ATTEMPTS) {
        const retryDelayMs = Math.pow(2, retriesUsed + 1) * 1000 // 2s → 4s → 8s
        setTimeout(() => syncOneTransaction(pendingTransaction), retryDelayMs)
      }
    } finally {
      syncInProgressIds.delete(pendingTransaction.id)
    }
  }

  async function uploadReceiptPhoto(blob, filename) {
    const formData = new FormData()
    formData.append('file', blob, filename)
    formData.append('is_private', 0)
    formData.append('folder', 'Home/Attachments')

    const response = await fetch('/api/method/upload_file', {
      method: 'POST',
      body: formData,
      headers: { 'X-Frappe-CSRF-Token': window.csrf_token },
    })

    if (!response.ok) {
      throw new Error('Receipt photo upload failed')
    }

    const responseData = await response.json()
    return responseData.message.file_url
  }

  // --- Periodic sync (fallback for environments without Background Sync API) ---

  function startPeriodicSync() {
    setInterval(() => {
      if (isOnline.value && !isSyncing.value) {
        syncAll()
      }
    }, PERIODIC_SYNC_INTERVAL_MS)
  }

  return {
    isOnline,
    isSyncing,
    syncStatus,
    lastSyncAt,
    setupOnlineOfflineListeners,
    registerBackgroundSync,
    syncAll,
    startPeriodicSync,
  }
})
