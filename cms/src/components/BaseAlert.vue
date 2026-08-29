<script setup>
import AppIcon from './AppIcon.vue'
const props = defineProps({
  type: { type: String, default: 'info' }, // ok | bad | warn | info
  title: { type: String, default: '' },
  dismissible: { type: Boolean, default: false },
})
const emit = defineEmits(['dismiss'])
const icon = { ok: 'check', bad: 'alert', warn: 'alert', info: 'drop' }
</script>

<template>
  <div class="alert" :class="'alert-' + type" role="alert">
    <AppIcon :name="icon[type] || 'drop'" :size="18" />
    <div style="flex:1">
      <strong v-if="title">{{ title }}</strong>
      <span v-if="title"> </span>
      <slot />
    </div>
    <button v-if="dismissible" class="modal-close" @click="emit('dismiss')" aria-label="Cerrar"><AppIcon name="close" :size="16" /></button>
  </div>
</template>
