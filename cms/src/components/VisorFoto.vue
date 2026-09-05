<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  src: { type: String, default: '' },
  titulo: { type: String, default: 'Evidencia' },
})
const emit = defineEmits(['update:show'])

function cerrar() { emit('update:show', false) }
function onKey(e) { if (e.key === 'Escape') cerrar() }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <teleport to="body">
    <div v-if="show" class="visor-overlay" @click.self="cerrar">
      <div class="visor-box">
        <div class="visor-head">
          <strong>{{ titulo }}</strong>
          <div style="display:flex; gap:.5rem">
            <a v-if="src" class="btn btn-ghost btn-sm" :href="src" target="_blank" rel="noopener">Abrir original</a>
            <button class="modal-close" @click="cerrar" aria-label="Cerrar"><AppIcon name="close" /></button>
          </div>
        </div>
        <img v-if="src" :src="src" alt="Evidencia" />
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.visor-overlay {
  position: fixed; inset: 0; background: rgba(20, 35, 55, .75);
  display: grid; place-items: center; padding: 1rem; z-index: 80;
}
.visor-box { background: #fff; border-radius: 12px; max-width: 860px; width: 100%; max-height: 90vh; display: flex; flex-direction: column; overflow: hidden; }
.visor-head { display: flex; align-items: center; justify-content: space-between; padding: .7rem 1rem; border-bottom: 1px solid var(--acr-borde); }
.visor-box img { width: 100%; max-height: calc(90vh - 60px); object-fit: contain; background: #0f1c2e; }
</style>
