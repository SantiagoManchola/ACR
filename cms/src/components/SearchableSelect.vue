<script setup>
import { ref, computed, watch } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number], default: null },
  options: { type: Array, default: () => [] }, // [{ value, label }]
  placeholder: { type: String, default: 'Seleccione…' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const root = ref(null)

const selected = computed(() => props.options.find((o) => o.value === props.modelValue) || null)

watch(selected, (s) => { if (!open.value) query.value = s ? s.label : '' }, { immediate: true })

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return props.options
  return props.options.filter((o) => String(o.label).toLowerCase().includes(q))
})

function onFocus() {
  if (props.disabled) return
  open.value = true
  query.value = ''
}
function choose(o) {
  emit('update:modelValue', o.value)
  query.value = o.label
  open.value = false
}
function clear() {
  emit('update:modelValue', null)
  query.value = ''
  open.value = false
}
function onBlur() {
  setTimeout(() => {
    open.value = false
    query.value = selected.value ? selected.value.label : ''
  }, 140)
}
function onKeydown(e) {
  if (e.key === 'Escape') open.value = false
}
</script>

<template>
  <div class="ss" ref="root">
    <div class="ss-control" :class="{ open, disabled }">
      <input
        class="ss-input"
        :value="query"
        :placeholder="placeholder"
        :disabled="disabled"
        autocomplete="off"
        role="combobox"
        :aria-expanded="open"
        @input="query = $event.target.value; open = true"
        @focus="onFocus"
        @blur="onBlur"
        @keydown="onKeydown"
      />
      <button v-if="clearable && modelValue != null && !disabled" type="button" class="ss-clear" @mousedown.prevent="clear" aria-label="Limpiar">
        <AppIcon name="close" :size="14" />
      </button>
      <AppIcon name="chevron" :size="16" class="ss-chev" />
    </div>
    <div v-if="open && !disabled" class="ss-drop">
      <button
        v-for="o in filtered"
        :key="o.value"
        type="button"
        class="ss-opt"
        :class="{ active: o.value === modelValue }"
        @mousedown.prevent="choose(o)"
      >{{ o.label }}</button>
      <p v-if="!filtered.length" class="ss-empty">Sin coincidencias.</p>
    </div>
  </div>
</template>

<style scoped>
.ss { position: relative; width: 100%; }
.ss-control {
  display: flex; align-items: center; gap: .35rem;
  border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm);
  background: #fff; padding: 0 .5rem;
}
.ss-control.open { border-color: var(--acr-azul); box-shadow: 0 0 0 3px rgba(33, 96, 173, .15); }
.ss-control.disabled { background: #F4F8FD; opacity: .8; }
.ss-input {
  flex: 1; border: none; outline: none; background: transparent;
  padding: .55rem .25rem; font-size: .9rem; font-family: inherit; color: var(--acr-texto);
}
.ss-chev { color: var(--acr-texto-suave); flex: none; transform: rotate(0deg); transition: transform .15s; }
.ss-control.open .ss-chev { transform: rotate(180deg); }
.ss-clear { background: none; border: none; cursor: pointer; color: var(--acr-texto-suave); display: grid; place-items: center; }
.ss-drop {
  position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 60;
  background: #fff; border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm);
  box-shadow: var(--acr-sombra); max-height: 240px; overflow-y: auto; padding: .25rem;
}
.ss-opt {
  display: block; width: 100%; text-align: left; border: none; background: none;
  padding: .5rem .6rem; border-radius: 6px; cursor: pointer; font-size: .88rem; color: var(--acr-texto);
  font-family: inherit;
}
.ss-opt:hover { background: var(--acr-azul-50); }
.ss-opt.active { background: var(--acr-azul-50); color: var(--acr-azul-700); font-weight: 600; }
.ss-empty { margin: 0; padding: .5rem .6rem; color: var(--acr-texto-suave); font-size: .82rem; }
</style>
