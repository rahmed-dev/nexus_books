<template>
  <BottomSheet title="Select Icon" @close="emit('close')">

    <!-- Search -->
    <div class="px-4 pb-3 pt-1">
      <input
        v-model="searchQuery"
        type="search"
        placeholder="Search icons…"
        class="w-full rounded-xl border border-outline-gray-2 bg-surface-gray-1 px-3 py-2 text-sm text-ink-gray-9 placeholder-ink-gray-4 focus:outline-none focus:ring-2 focus:ring-ink-gray-4"
        autofocus
      />
    </div>

    <!-- Icon grid -->
    <div class="px-4 pb-4">
      <p v-if="visibleIcons.length === 0" class="py-8 text-center text-sm text-ink-gray-5">
        No icons found for "{{ searchQuery }}"
      </p>

      <template v-else-if="searchQuery.trim()">
        <!-- Flat grid when searching -->
        <div class="grid grid-cols-7 gap-1">
          <button
            v-for="name in visibleIcons"
            :key="name"
            type="button"
            class="flex items-center justify-center rounded-xl p-2.5 transition-transform active:scale-90"
            :class="name === modelValue ? 'ring-2 ring-ink-gray-9 bg-surface-gray-2' : 'hover:bg-surface-gray-1'"
            @click="onSelect(name)"
          >
            <span class="block h-7 w-7 text-ink-gray-8 [&>svg]:h-full [&>svg]:w-full" v-html="getIconSvg(name)" />
          </button>
        </div>
      </template>

      <template v-else>
        <!-- Grouped view -->
        <div v-for="(names, group) in lucideIconGroups" :key="group" class="mb-5">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-ink-gray-5">{{ group }}</p>
          <div class="grid grid-cols-7 gap-1">
            <button
              v-for="name in names"
              :key="name"
              type="button"
              class="flex items-center justify-center rounded-xl p-2.5 transition-transform active:scale-90"
              :class="name === modelValue ? 'ring-2 ring-ink-gray-9 bg-surface-gray-2' : 'hover:bg-surface-gray-1'"
              @click="onSelect(name)"
            >
              <span class="block h-7 w-7 text-ink-gray-8 [&>svg]:h-full [&>svg]:w-full" v-html="getIconSvg(name)" />
            </button>
          </div>
        </div>
      </template>
    </div>

  </BottomSheet>
</template>

<script setup>
import { ref, computed } from 'vue'
import { lucideIconGroups, allLucideIconNames } from '@/data/lucide-icons'
import { getIconSvg } from '@/utils/icons'
import BottomSheet from '@/components/BottomSheet.vue'

const props = defineProps({
  modelValue: { type: String, default: null },
})

const emit = defineEmits(['select', 'close'])

const searchQuery = ref('')

const visibleIcons = computed(() => {
  const needle = searchQuery.value.trim().toLowerCase()
  if (!needle) return allLucideIconNames
  return allLucideIconNames.filter((name) => name.includes(needle))
})

function onSelect(iconName) {
  emit('select', iconName)
  emit('close')
}
</script>
