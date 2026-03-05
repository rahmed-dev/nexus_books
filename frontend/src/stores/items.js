import { defineStore } from 'pinia'
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { openNexusDB } from '@/utils/db'

export const useItemStore = defineStore('items', () => {
  const items = ref([])
  const isLoading = ref(false)

  // --- Public actions ---

  async function loadItems() {
    isLoading.value = true
    try {
      const fetchedItems = await fetchItemsFromFrappe()
      items.value = fetchedItems
      cacheItemsInDB(fetchedItems).catch(() => {})
    } catch {
      // Network / API failed — fall back to IndexedDB cache
      items.value = await loadItemsFromCache()
    } finally {
      isLoading.value = false
    }
  }

  // --- Private helpers ---

  async function fetchItemsFromFrappe() {
    const response = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_items',
    })
    return response || []
  }

  async function loadItemsFromCache() {
    const db = await openNexusDB()
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['cached_items'], 'readonly')
      const store = idbTx.objectStore('cached_items')
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async function cacheItemsInDB(itemList) {
    const db = await openNexusDB()
    const idbTx = db.transaction(['cached_items'], 'readwrite')
    const store = idbTx.objectStore('cached_items')

    await new Promise((resolve, reject) => {
      const clearRequest = store.clear()
      clearRequest.onsuccess = resolve
      clearRequest.onerror = () => reject(clearRequest.error)
    })

    const cachedAt = new Date().toISOString()
    for (const item of itemList) {
      await new Promise((resolve, reject) => {
        const addRequest = store.add({ ...item, cached_at: cachedAt })
        addRequest.onsuccess = resolve
        addRequest.onerror = () => reject(addRequest.error)
      })
    }
  }

  return {
    items,
    isLoading,
    loadItems,
  }
})
