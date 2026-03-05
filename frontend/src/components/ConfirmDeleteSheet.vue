<template>
  <BottomSheet :is-open="isOpen" max-height="auto" @close="emit('close')">

    <div class="px-4 pb-6 pt-2">
      <h2 class="text-base font-semibold text-ink-gray-9">Delete transaction?</h2>
      <p class="mt-1 text-sm text-ink-gray-5">This cannot be undone.</p>

      <!-- Transaction summary -->
      <div v-if="transaction" class="mt-4 flex items-center gap-3 rounded-xl bg-surface-gray-1 px-4 py-3">
        <span
          class="text-sm font-medium"
          :class="transaction.transaction_type === 'Income' ? 'text-green-600' : 'text-ink-gray-9'"
        >
          {{ transaction.transaction_type === 'Income' ? '+' : '-' }}{{ formattedAmount }}
        </span>
        <span class="text-sm text-ink-gray-6">
          {{ transaction.category_name || transaction.category_label || transaction.category || 'Uncategorised' }}
        </span>
      </div>

      <!-- Actions -->
      <div class="mt-5 flex gap-3">
        <Button variant="subtle" class="flex-1" @click="emit('close')">Cancel</Button>
        <Button variant="solid" class="flex-1 !bg-red-600 hover:!bg-red-700" :loading="isDeleting" @click="emit('confirm')">
          Delete
        </Button>
      </div>
    </div>

  </BottomSheet>
</template>

<script setup>
import { computed } from 'vue'
import BottomSheet from '@/components/BottomSheet.vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  transaction: { type: Object, default: null },
  isDeleting: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'confirm'])

const formattedAmount = computed(() =>
  Number(props.transaction?.amount || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }),
)
</script>
