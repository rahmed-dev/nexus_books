/**
 * Shared IndexedDB connection for nexus_books_db.
 * Singleton pattern — all stores import openNexusDB() from here.
 * Schema matches the vanilla-JS OfflineManager schema exactly.
 */

const DB_NAME = 'nexus_books_db'
const DB_VERSION = 3

let dbConnectionPromise = null

export function openNexusDB() {
  if (!dbConnectionPromise) {
    dbConnectionPromise = new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION)

      request.onerror = () => reject(request.error)
      request.onsuccess = () => resolve(request.result)

      request.onupgradeneeded = (event) => {
        const db = event.target.result
        const previousVersion = event.oldVersion

        // v1 → v2: cached_parties and cached_categories used keyPath:'id' but
        // Frappe returns records keyed by 'name'. Delete and recreate both stores.
        if (previousVersion < 2) {
          if (db.objectStoreNames.contains('cached_parties')) {
            db.deleteObjectStore('cached_parties')
          }
          if (db.objectStoreNames.contains('cached_categories')) {
            db.deleteObjectStore('cached_categories')
          }
        }

        if (!db.objectStoreNames.contains('transactions')) {
          const transactionStore = db.createObjectStore('transactions', {
            keyPath: 'id',
            autoIncrement: true,
          })
          transactionStore.createIndex('sync_status', 'sync_status', { unique: false })
          transactionStore.createIndex('date', 'date', { unique: false })
          transactionStore.createIndex('created_at', 'created_at', { unique: false })
        }

        if (!db.objectStoreNames.contains('cached_parties')) {
          const partyStore = db.createObjectStore('cached_parties', { keyPath: 'name' })
          partyStore.createIndex('party_type', 'party_type', { unique: false })
          partyStore.createIndex('transaction_count', 'transaction_count', { unique: false })
        }

        if (!db.objectStoreNames.contains('cached_categories')) {
          const categoryStore = db.createObjectStore('cached_categories', { keyPath: 'name' })
          categoryStore.createIndex('category_type', 'category_type', { unique: false })
          categoryStore.createIndex('is_active', 'is_active', { unique: false })
        }

        if (!db.objectStoreNames.contains('app_settings')) {
          db.createObjectStore('app_settings', { keyPath: 'key' })
        }

        // v3: offline caches for items and nexus accounts
        if (previousVersion < 3) {
          if (!db.objectStoreNames.contains('cached_items')) {
            db.createObjectStore('cached_items', { keyPath: 'name' })
          }
          if (!db.objectStoreNames.contains('cached_nexus_accounts')) {
            db.createObjectStore('cached_nexus_accounts', { keyPath: 'name' })
          }
        }
      }
    })
  }
  return dbConnectionPromise
}
