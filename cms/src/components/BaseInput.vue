<script setup>
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: true },
})
const emit = defineEmits(['update:modelValue'])

const mostrarLimpiar = () => props.clearable && !props.disabled &&
  props.modelValue !== '' && props.modelValue !== null && props.modelValue !== undefined

function onInput(e) {
  const v = e.target.value
  emit('update:modelValue', props.type === 'number' && v !== '' ? Number(v) : v)
}
function limpiar() { emit('update:modelValue', '') }
</script>

<template>
  <div class="base-input">
    <input
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
.input-clear {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--acr-texto-suave);
  display: grid; place-items: center; padding: 3px; border-radius: 50%;
}
.input-clear:hover { color: var(--acr-bad); background: var(--acr-bad-bg); }
</style>
