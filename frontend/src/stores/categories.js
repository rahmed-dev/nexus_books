import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { frappeRequest } from 'frappe-ui'
import { openNexusDB } from '@/utils/db'

export const useCategoryStore = defineStore('categories', () => {
  const categories = ref([])
  const isLoading = ref(false)

  const activeCategories = computed(() => categories.value.filter((c) => c.is_active))
  const incomeCategories = computed(() =>
    activeCategories.value.filter((c) => c.category_type === 'Income'),
  )
  const expenseCategories = computed(() =>
    activeCategories.value.filter((c) => c.category_type === 'Expense'),
  )

  // --- Public actions ---

  async function loadCategories() {
    isLoading.value = true
    try {
      const fetchedCategories = await fetchCategoriesFromFrappe()
      categories.value = fetchedCategories
      cacheCategoriesInDB(fetchedCategories).catch(() => {})
    } catch {
      // Network / API failed — fall back to IndexedDB cache
      categories.value = await loadCategoriesFromCache()
    } finally {
      isLoading.value = false
    }
  }

  async function loadCategoriesFromCache(categoryType = null) {
    const db = await openNexusDB()
    return new Promise((resolve, reject) => {
      const idbTx = db.transaction(['cached_categories'], 'readonly')
      const store = idbTx.objectStore('cached_categories')

      const request = categoryType
        ? store.index('category_type').getAll(categoryType)
        : store.getAll()

      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error)
    })
  }

  // --- Private helpers ---

  async function fetchCategoriesFromFrappe() {
    const response = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_transaction_categories',
    })
    return response || []
  }

  async function cacheCategoriesInDB(categoryList) {
    const db = await openNexusDB()
    const idbTx = db.transaction(['cached_categories'], 'readwrite')
    const store = idbTx.objectStore('cached_categories')

    await new Promise((resolve, reject) => {
      const clearRequest = store.clear()
      clearRequest.onsuccess = resolve
      clearRequest.onerror = () => reject(clearRequest.error)
    })

    const cachedAt = new Date().toISOString()
    for (const category of categoryList) {
      await new Promise((resolve, reject) => {
        const addRequest = store.add({ ...category, cached_at: cachedAt })
        addRequest.onsuccess = resolve
        addRequest.onerror = () => reject(addRequest.error)
      })
    }
  }

  async function createCategory(categoryData) {
    const created = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.create_category',
      params: {
        category_name: categoryData.category_name,
        category_type: categoryData.category_type,
        color: categoryData.color || null,
        icon: categoryData.icon || null,
        gl_account: categoryData.gl_account || null,
      },
    })
    await loadCategories()
    return created
  }

  async function updateCategory(docname, categoryData) {
    const updated = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.update_category',
      params: {
        category: docname,
        category_name: categoryData.category_name,
        category_type: categoryData.category_type,
        color: categoryData.color || null,
        icon: categoryData.icon || null,
        gl_account: categoryData.gl_account || null,
      },
    })
    await loadCategories()
    return updated
  }

  async function toggleActive(docname) {
    const result = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.toggle_category_active',
      params: { category: docname },
    })
    // Update in-place to avoid a full reload flash
    const target = categories.value.find((c) => c.name === docname)
    if (target) target.is_active = result.is_active
    return result
  }

  return {
    categories,
    isLoading,
    activeCategories,
    incomeCategories,
    expenseCategories,
    loadCategories,
    loadCategoriesFromCache,
    createCategory,
    updateCategory,
    toggleActive,
  }
})
