<template>
  <div class="flex items-center gap-1 px-4 pb-2 pt-6">
    <button
      v-if="backTo"
      type="button"
      class="-ml-1 mr-1 p-1 text-ink-gray-7 active:text-ink-gray-9"
      @click="goBack"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
    </button>
    <h1 class="text-lg font-semibold text-ink-gray-9">{{ title }}</h1>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: { type: String, required: true },
  backTo: { type: String, default: null },
})

const router = useRouter()

function goBack() {
  router.push(props.backTo)
}
</script>
