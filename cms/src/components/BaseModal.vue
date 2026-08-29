<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: '560' },
})
const emit = defineEmits(['update:modelValue', 'close'])

function close() { emit('update:modelValue', false); emit('close') }

function onKey(e) { if (e.key === 'Escape') close() }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>

<template>
  <teleport to="body">
    <div class="modal-overlay" v-if="modelValue" @click.self="close">
      <div class="modal" :style="{ maxWidth: size + 'px' }">
        <div class="modal-head">
          <h3>{{ title }}</h3>
          <button class="modal-close" @click="close" aria-label="Cerrar"><AppIcon name="close" /></button>
        </div>
        <div class="modal-body"><slot /></div>
        <div class="modal-foot" v-if="$slots.footer"><slot name="footer" /></div>
      </div>
    </div>
  </teleport>
</template>
