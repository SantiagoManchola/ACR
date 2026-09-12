<script setup>
import AppIcon from './AppIcon.vue'
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])

const inputEl = ref(null)

const mostrarLimpiar = () => props.clearable && !props.disabled &&
  props.modelValue !== '' && props.modelValue !== null && props.modelValue !== undefined

function onInput(e) {
  const v = e.target.value
  emit('update:modelValue', props.type === 'number' && v !== '' ? Number(v) : v)
}
function limpiar() { emit('update:modelValue', '') }

function abrirCalendario() {
  const el = inputEl.value
  if (!el) return
  if (typeof el.showPicker === 'function') { try { el.showPicker() } catch { el.focus() } }
  else el.focus()
}
</script>

<template>
  <div class="base-input" :class="{ 'is-date': type === 'date' }">
    <button
      v-if="type === 'date'"
      type="button"
      class="input-date-icon"
      aria-label="Abrir calendario"
      title="Abrir calendario"
      :disabled="disabled"
      @click="abrirCalendario"
    ><AppIcon name="calendar" :size="16" /></button>
    <input
      ref="inputEl"
      class="input"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      @input="onInput"
    />
    <button
      v-if="mostrarLimpiar"
      type="button"
      class="input-clear"
      aria-label="Limpiar campo"
      title="Limpiar"
      @click="limpiar"
    ><AppIcon name="close" :size="13" /></button>
  </div>
</template>

<style scoped>
.base-input { position: relative; width: 100%; }
.base-input .input { padding-right: 2rem; }
.base-input.is-date .input { padding-left: 2.4rem; }
.input-date-icon {
  position: absolute; left: 8px; top: 50%; transform: translateY(-50%);
  background: none; border: none; padding: 2px; cursor: pointer;
  color: var(--acr-texto-suave); display: grid; place-items: center; border-radius: 4px;
}
.input-date-icon:hover:not(:disabled) { color: var(--acr-azul); }
.input-date-icon:disabled { cursor: not-allowed; opacity: .6; }
.input-clear {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--acr-texto-suave);
  display: grid; place-items: center; padding: 3px; border-radius: 50%;
}
.input-clear:hover { color: var(--acr-bad); background: var(--acr-bad-bg); }
</style>
