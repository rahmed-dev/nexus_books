<template>
  <!--
    Mobile-first app shell.
    - Full viewport height, no scroll bounce
    - Content slot scrolls within the safe area
    - Bottom safe area reserved for home indicator (env(safe-area-inset-bottom))
    - Max width centered for tablets viewing in portrait
  -->
  <div class="flex h-full flex-col bg-surface-white">
    <!-- Main scrollable content area -->
    <main class="relative flex-1 overflow-y-auto overscroll-contain">
      <slot />
    </main>

    <!-- Bottom navigation bar with safe area padding -->
    <nav
      class="flex shrink-0 items-center justify-around border-t border-outline-gray-1 bg-surface-white px-2"
      :style="{ paddingBottom: 'max(0.75rem, env(safe-area-inset-bottom))' }"
    >
      <slot name="bottom-nav" />
    </nav>
  </div>
</template>
