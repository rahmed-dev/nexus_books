import './index.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import {
  FrappeUI,
  Button,
  Input,
  FormControl,
  Dialog,
  Badge,
  Autocomplete,
  setConfig,
  frappeRequest,
} from 'frappe-ui'

const globalComponents = {
  Button,
  Input,
  FormControl,
  Dialog,
  Badge,
  Autocomplete,
}

const pinia = createPinia()
const app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(pinia)
app.use(router)

for (const componentName in globalComponents) {
  app.component(componentName, globalComponents[componentName])
}

if (import.meta.env.DEV) {
  frappeRequest({ url: '/api/method/nexus_books.nexus_books.www.nexus.get_context_for_dev' })
    .then((values) => {
      for (const key in values) {
        window[key] = values[key]
      }
    })
    .catch(() => {
      // Boot data unavailable in dev — app still works for component development
    })
    .finally(() => {
      app.mount('#app')
    })
} else {
  app.mount('#app')
}
