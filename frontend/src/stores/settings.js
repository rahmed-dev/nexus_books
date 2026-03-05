import { defineStore } from 'pinia'
import { ref } from 'vue'
import { frappeRequest } from 'frappe-ui'

export const useSettingsStore = defineStore('settings', () => {
  const currency = ref('PKR')
  const currencySymbol = ref('Rs.')

  async function loadSettings() {
    try {
      const result = await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.get_default_currency',
      })
      currency.value = result?.currency || 'PKR'
      currencySymbol.value = result?.symbol || 'Rs.'
    } catch {
      // Keep defaults — PKR / Rs.
    }
  }

  return { currency, currencySymbol, loadSettings }
})
