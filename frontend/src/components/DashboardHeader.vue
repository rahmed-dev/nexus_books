<template>
  <div class="px-1 pt-2 pb-1">
    <p class="text-2xl font-bold text-ink-gray-9">Welcome! {{ fullName }}</p>
  </div>
</template>

<script setup>
const fullName = window.full_name || window.user_id || 'there'
</script>
