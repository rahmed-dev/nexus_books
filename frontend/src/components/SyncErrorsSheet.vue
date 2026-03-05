<template>
  <BottomSheet title="ERPNext Sync Errors" @close="emit('close')">

    <!-- Loading -->
    <div v-if="isLoading" class="py-10 text-center text-sm text-ink-gray-5">
      Loading…
    </div>

    <!-- Empty state -->
    <EmptyState
      v-else-if="!failedTransactions.length"
      title="No sync errors"
      subtitle="All transactions have been posted to ERPNext"
    />

    <!-- Error list -->
    <div v-else class="divide-y divide-outline-gray-1">
      <div
        v-for="txn in failedTransactions"
        :key="txn.name"
        class="px-4 py-3"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-ink-gray-9">
              {{ txn.transaction_type }} · {{ formatAmount(txn.amount) }}
            </p>
            <p class="text-xs text-ink-gray-5">{{ formatDate(txn.date) }}</p>
            <p class="mt-1 text-xs text-red-500 break-words">{{ txn.gl_error || 'Unknown error' }}</p>
          </div>
          <button
            type="button"
            class="shrink-0 rounded-lg border border-outline-gray-2 px-3 py-1.5 text-xs font-medium text-ink-gray-7 active:bg-surface-gray-1"
            :disabled="retryingNames.has(txn.name)"
            @click="retrySingle(txn.name)"
          >
            {{ retryingNames.has(txn.name) ? 'Retrying…' : 'Retry' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Footer: Retry All -->
    <template v-if="failedTransactions.length" #footer>
      <div class="px-4 py-3">
        <button
          type="button"
          class="w-full rounded-xl bg-surface-gray-7 py-3 text-sm font-semibold text-white active:bg-surface-gray-6 disabled:opacity-50"
          :disabled="isRetryingAll"
          @click="retryAll"
        >
          {{ isRetryingAll ? 'Retrying all…' : `Retry All (${failedTransactions.length})` }}
        </button>
      </div>
    </template>

  </BottomSheet>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { frappeRequest } from 'frappe-ui'
import BottomSheet from '@/components/BottomSheet.vue'
import EmptyState from '@/components/EmptyState.vue'

const emit = defineEmits(['close', 'count-changed'])

const isLoading = ref(false)
const failedTransactions = ref([])
const retryingNames = ref(new Set())
const isRetryingAll = ref(false)

async function loadFailedTransactions() {
  isLoading.value = true
  try {
    failedTransactions.value =
      (await frappeRequest({
        url: '/api/method/nexus_books.nexus_books.api.get_failed_gl_transactions',
        params: { limit: 50 },
      })) ?? []
    emit('count-changed', failedTransactions.value.length)
  } catch {
    // Silently fail — sheet shows empty state
  } finally {
    isLoading.value = false
  }
}

async function retrySingle(name) {
  retryingNames.value = new Set([...retryingNames.value, name])
  try {
    await frappeRequest({
      url: '/api/method/nexus_books.nexus_books.api.retry_gl_sync',
      params: { name },
    })
    // Remove from list — scheduler will pick it up
    failedTransactions.value = failedTransactions.value.filter((t) => t.name !== name)
    emit('count-changed', failedTransactions.value.length)
  } catch {
    // Keep in list — user sees it failed
  } finally {
    const updated = new Set(retryingNames.value)
    updated.delete(name)
    retryingNames.value = updated
  }
}

async function retryAll() {
  isRetryingAll.value = true
  const names = failedTransactions.value.map((t) => t.name)
  await Promise.allSettled(names.map((name) => retrySingle(name)))
  isRetryingAll.value = false
}

function formatAmount(amount) {
  return Number(amount || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(loadFailedTransactions)
</script>
