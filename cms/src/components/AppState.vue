<script setup>
import AppIcon from './AppIcon.vue'
const props = defineProps({
  mode: { type: String, default: '' }, // loading | empty | error
  message: { type: String, default: '' },
})
</script>

<template>
  <div class="state-block">
    <div v-if="mode === 'loading'" class="spinner"></div>
    <AppIcon v-else-if="mode === 'empty'" name="search" :size="30" />
    <AppIcon v-else-if="mode === 'error'" name="alert" :size="30" />
    <p style="margin:.3rem 0 0">{{ message }}</p>
    <slot />
  </div>
</template>
