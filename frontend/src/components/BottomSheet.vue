<template>
  <Teleport to="body">
    <Transition name="nb-fade">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 bg-black/40"
        @click="emit('close')"
      />
    </Transition>

    <Transition name="nb-slide-up">
      <div
        v-if="isOpen"
        class="fixed inset-x-0 bottom-0 z-50 flex flex-col rounded-t-2xl bg-surface-white"
        :style="{ maxHeight, paddingBottom: 'env(safe-area-inset-bottom)' }"
      >
        <!-- Drag handle -->
        <div class="flex justify-center pt-3 pb-1">
          <div class="h-1 w-10 rounded-full bg-outline-gray-2" />
        </div>

        <!-- Standard header (rendered when title prop is provided) -->
        <div v-if="title" class="flex items-center justify-between px-4 py-2">
          <h2 class="text-base font-semibold text-ink-gray-9">{{ title }}</h2>
          <button
            type="button"
            class="p-1 text-ink-gray-5 active:text-ink-gray-9"
            @click="emit('close')"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Scrollable body -->
        <div class="flex-1 overflow-y-auto">
          <slot />
        </div>

        <!-- Footer (rendered only when footer slot is used) -->
        <div v-if="$slots.footer" class="border-t border-outline-gray-1">
          <slot name="footer" />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  isOpen: { type: Boolean, default: true },
  title: { type: String, default: null },
  maxHeight: { type: String, default: '85vh' },
})

const emit = defineEmits(['close'])
</script>

<style scoped>
.nb-slide-up-enter-active,
.nb-slide-up-leave-active {
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.nb-slide-up-enter-from,
.nb-slide-up-leave-to {
  transform: translateY(100%);
}
.nb-fade-enter-active,
.nb-fade-leave-active {
  transition: opacity 0.25s ease;
}
.nb-fade-enter-from,
.nb-fade-leave-to {
  opacity: 0;
}
</style>
