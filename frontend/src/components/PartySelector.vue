<template>
  <Autocomplete
    :options="partyOptions"
    :value="modelValue"
    :placeholder="`Search ${partyTypeLabel}…`"
    @change="onSelect"
  />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { frappeRequest } from 'frappe-ui'

const props = defineProps({
  modelValue: {
    type: String,
    default: null,
  },
  partyType: {
    type: String,
    default: 'Customer', // 'Customer' | 'Supplier'
  },
})

const emit = defineEmits(['update:modelValue'])

const cachedParties = ref([])

const partyTypeLabel = computed(() => (props.partyType === 'Customer' ? 'customer' : 'supplier'))

const partyOptions = computed(() =>
  cachedParties.value.map((party) => ({
    value: party.name,
    label: party.party_name || party.name,
  })),
)

async function loadParties() {
  try {
    const response = await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.get_cached_parties',
      params: { party_type: props.partyType },
    })
    cachedParties.value = response || []
  } catch {
    // Offline — autocomplete options will be empty; user can type a value manually
  }
}

function onSelect(option) {
  emit('update:modelValue', option?.value ?? null)
}

onMounted(loadParties)
watch(() => props.partyType, loadParties)
</script>
