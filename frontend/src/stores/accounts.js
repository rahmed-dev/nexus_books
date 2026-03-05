import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { openNexusDB } from '@/utils/db'

export const useAccountStore = defineStore('accounts', () => {
  const accounts = ref([])
  const isLoading = ref(false)

  const defaultAccount = computed(() => accounts.value.find((a) => a.is_default) || null)
  const totalBalance = computed(() =>
    accounts.value.reduce((sum, account) => sum + (account.balance || 0), 0),
  )

  // --- Public actions ---

  async function loadAccounts() {
    isLoading.value = true
    try {
      const fetchedAccounts = await fetchAccountsFromFrappe()
      accounts.value = fetchedAccounts
      cacheAccountsInDB(fetchedAccounts).catch(() => {})
    } catch {
      // Network / API failed — fall back to IndexedDB cache
      accounts.value = await loadAccountsFromCache()
    } finally {
      isLoading.value = false
    }
  }

  async function createAccount(account_name, account_type, is_default = false) {
    await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.create_nexus_account',
      params: { account_name, account_type, is_default: is_default ? 1 : 0 },
    })
    await loadAccounts()
  }

  async function updateAccount(name, account_name, account_type, is_default = false) {
    await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.update_nexus_account',
      params: { name, account_name, account_type, is_default: is_default ? 1 : 0 },
    })
    await loadAccounts()
  }

  async function setDefault(name) {
    await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.set_default_nexus_account',
      params: { name },
    })
    await loadAccounts()
  }

  // --- Private helpers ---

  async function fetchAccountsFromFrappe() {
    const response = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_nexus_accounts',
    })
    return response || []
  }

  async function loadAccountsFromCache() {
    const db = await openNexusDB()
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['cached_nexus_accounts'], 'readonly')
      const store = idbTx.objectStore('cached_nexus_accounts')
      const request = store.getAll()
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  async function cacheAccountsInDB(accountList) {
    const db = await openNexusDB()
    const idbTx = db.transaction(['cached_nexus_accounts'], 'readwrite')
    const store = idbTx.objectStore('cached_nexus_accounts')

    await new Promise((resolve, reject) => {
      const clearRequest = store.clear()
      clearRequest.onsuccess = resolve
      clearRequest.onerror = () => reject(clearRequest.error)
    })

    const cachedAt = new Date().toISOString()
    for (const account of accountList) {
      await new Promise((resolve, reject) => {
        const addRequest = store.add({ ...account, cached_at: cachedAt })
        addRequest.onsuccess = resolve
        addRequest.onerror = () => reject(addRequest.error)
      })
    }
  }

  return {
    accounts,
    isLoading,
    defaultAccount,
    totalBalance,
    loadAccounts,
    createAccount,
    updateAccount,
    setDefault,
  }
})
