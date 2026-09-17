<script setup>
import BaseModal from './BaseModal.vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: 'Confirmar' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: 'Confirmar' },
  danger: { type: Boolean, default: true },
  // Peticiones en curso: el botón confirmar deshabilita y muestra carga
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['update:show', 'confirm', 'cancel'])

function close() { if (!props.loading) { emit('update:show', false); emit('cancel') } }
function confirm() { if (!props.loading) emit('confirm') }
</script>

<template>
  <BaseModal :model-value="show" @update:model-value="emit('update:show', $event)" :title="title" size="420">
    <div class="confirm-body">
      <span class="confirm-icon" :class="{ danger }"><AppIcon :name="danger ? 'alert' : 'check'" :size="22" /></span>
      <p class="confirm-msg">{{ message }}</p>
    </div>
    <template #footer>
      <button class="btn btn-ghost" :disabled="loading" @click="close">Cancelar</button>
      <button class="btn" :class="danger ? 'btn-danger' : 'btn-primary'" :disabled="loading" @click="confirm">
        <span v-if="loading" class="spinner"></span>{{ loading ? 'Procesando…' : confirmText }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.confirm-body { display: flex; gap: .8rem; align-items: flex-start; padding: .2rem 0 .6rem; }
.confirm-icon { width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center; flex: none; }
.confirm-icon.danger { background: var(--acr-bad-bg); color: var(--acr-bad); }
.confirm-icon:not(.danger) { background: var(--acr-ok-bg); color: var(--acr-ok); }
.confirm-msg { margin: 0; color: var(--acr-texto); font-size: .92rem; line-height: 1.5; }
</style>
