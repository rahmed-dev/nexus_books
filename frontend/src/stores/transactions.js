import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { openNexusDB } from '@/utils/db'

export const useTransactionStore = defineStore('transactions', () => {
  const transactions = ref([])
  const pendingCount = ref(0)
  const isLoading = ref(false)

  const hasPendingTransactions = computed(() => pendingCount.value > 0)

  // --- Public actions ---

  async function loadRecentTransactions(limit = 50) {
    isLoading.value = true
    try {
      const db = await openNexusDB()
      transactions.value = await fetchAllTransactionsNewestFirst(db, limit)
      await refreshPendingCount(db)
    } finally {
      isLoading.value = false
    }
  }

  async function addTransaction(transactionData) {
    const db = await openNexusDB()
    const transactionToSave = {
      ...transactionData,
      sync_status: 'pending',
      created_at: new Date().toISOString(),
      retry_count: 0,
    }
    const newId = await insertTransactionIntoDB(db, transactionToSave)
    await loadRecentTransactions()
    return newId
  }

  async function getPendingTransactions() {
    const db = await openNexusDB()
    return fetchTransactionsByStatus(db, 'pending')
  }

  async function getUnsyncedTransactions() {
    const db = await openNexusDB()
    const [pendingTransactions, failedTransactions] = await Promise.all([
      fetchTransactionsByStatus(db, 'pending'),
      fetchTransactionsByStatus(db, 'failed'),
    ])
    return [...pendingTransactions, ...failedTransactions].sort(
      (a, b) => new Date(b.created_at) - new Date(a.created_at),
    )
  }

  async function markTransactionSyncing(transactionId) {
    const db = await openNexusDB()
    await patchTransactionInDB(db, transactionId, { sync_status: 'syncing' })
  }

  async function markTransactionSynced(transactionId, referenceDoctype, referenceName) {
    const db = await openNexusDB()
    await patchTransactionInDB(db, transactionId, {
      sync_status: 'synced',
      synced_at: new Date().toISOString(),
      reference_doctype: referenceDoctype,
      reference_name: referenceName,
      sync_error: null,
    })
    await refreshPendingCount(db)
  }

  async function markTransactionFailed(transactionId, errorMessage, currentRetryCount) {
    const db = await openNexusDB()
    await patchTransactionInDB(db, transactionId, {
      sync_status: 'failed',
      sync_error: errorMessage,
      retry_count: currentRetryCount + 1,
    })
  }

  async function deleteIdbTransaction(transactionId) {
    const db = await openNexusDB()
    await removeTransactionFromDB(db, transactionId)
    await loadRecentTransactions()
  }

  async function updateIdbTransaction(transactionId, updatedData) {
    const db = await openNexusDB()
    await patchTransactionInDB(db, transactionId, {
      ...updatedData,
      sync_status: 'pending', // re-queue for sync after edit
    })
    await loadRecentTransactions()
  }

  async function cacheParties(partyList) {
    const db = await openNexusDB()
    const idbTx = db.transaction(['cached_parties'], 'readwrite')
    const store = idbTx.objectStore('cached_parties')

    await new Promise((resolve, reject) => {
      const clearRequest = store.clear()
      clearRequest.onsuccess = resolve
      clearRequest.onerror = () => reject(clearRequest.error)
    })

    const cachedAt = new Date().toISOString()
    for (const party of partyList) {
      await new Promise((resolve, reject) => {
        const addRequest = store.add({ ...party, cached_at: cachedAt })
        addRequest.onsuccess = resolve
        addRequest.onerror = () => reject(addRequest.error)
      })
    }
  }

  async function getCachedPartiesByType(partyType) {
    const db = await openNexusDB()
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['cached_parties'], 'readonly')
      const request = idbTx.objectStore('cached_parties').index('party_type').getAll(partyType)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  // --- Private IDB helpers ---

  function fetchAllTransactionsNewestFirst(db, limit) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readonly')
      const request = idbTx.objectStore('transactions').index('created_at').openCursor(null, 'prev')
      const results = []
      let count = 0

      request.onsuccess = (event) => {
        const cursor = event.target.result
        if (cursor && count < limit) {
          results.push(cursor.value)
          count++
          cursor.continue()
        } else {
          resolve(results)
        }
      }
      request.onerror = () => reject(request.error)
    })
  }

  function insertTransactionIntoDB(db, transactionData) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readwrite')
      const request = idbTx.objectStore('transactions').add(transactionData)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  function fetchTransactionsByStatus(db, syncStatus) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readonly')
      const request = idbTx.objectStore('transactions').index('sync_status').getAll(syncStatus)
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  function patchTransactionInDB(db, transactionId, updates) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readwrite')
      const store = idbTx.objectStore('transactions')
      const getRequest = store.get(transactionId)

      getRequest.onsuccess = () => {
        const existingTransaction = getRequest.result
        if (!existingTransaction) {
          reject(new Error(`Transaction ${transactionId} not found in IndexedDB`))
          return
        }
        const updatedTransaction = { ...existingTransaction, ...updates }
        const putRequest = store.put(updatedTransaction)
        putRequest.onsuccess = () => resolve(updatedTransaction)
        putRequest.onerror = () => reject(putRequest.error)
      }
      getRequest.onerror = () => reject(getRequest.error)
    })
  }

  function removeTransactionFromDB(db, transactionId) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readwrite')
      const request = idbTx.objectStore('transactions').delete(transactionId)
      request.onsuccess = () => resolve()
      request.onerror = () => reject(request.error)
    })
  }

  function refreshPendingCount(db) {
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['transactions'], 'readonly')
      const request = idbTx.objectStore('transactions').index('sync_status').count('pending')
      request.onsuccess = () => {
        pendingCount.value = request.result
        resolve()
      }
      request.onerror = () => reject(request.error)
    })
  }

  return {
    transactions,
    pendingCount,
    isLoading,
    hasPendingTransactions,
    loadRecentTransactions,
    addTransaction,
    deleteIdbTransaction,
    updateIdbTransaction,
    getPendingTransactions,
    getUnsyncedTransactions,
    markTransactionSyncing,
    markTransactionSynced,
    markTransactionFailed,
    cacheParties,
    getCachedPartiesByType,
  }
})
