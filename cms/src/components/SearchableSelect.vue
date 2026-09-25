<script setup>
import { ref, computed, watch, nextTick, onBeforeUnmount } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: [String, Number, Boolean], default: null },
  options: { type: Array, default: () => [] }, // [{ value, label }]
  placeholder: { type: String, default: 'Seleccione…' },
  disabled: { type: Boolean, default: false },
  clearable: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const query = ref('')
const root = ref(null)
const control = ref(null)
const drop = ref(null)
const dropStyle = ref({})

const selected = computed(() => props.options.find((o) => o.value === props.modelValue) || null)

watch(selected, (s) => { if (!open.value) query.value = s ? s.label : '' }, { immediate: true })

/* Búsqueda permisiva: cada palabra debe aparecer (en cualquier orden) e
   ignora mayúsculas y tildes. Ej.: «simon acosta» encuentra «ACOSTA MARTINEZ SIMON». */
function normalizar(s) {
  return String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
}
const filtered = computed(() => {
  const tokens = normalizar(query.value).trim().split(/\s+/).filter(Boolean)
  if (!tokens.length) return props.options
  return props.options.filter((o) => {
    // `search` permite encontrar la opción por datos que no se muestran
    // (p. ej. serial o dirección) y `sub` es la línea secundaria visible.
    const texto = normalizar([o.label, o.search, o.sub].filter(Boolean).join(' '))
    return tokens.every((t) => texto.includes(t))
  })
})

/* El panel se teletransporta al body y se posiciona con coordenadas fijas:
   así nunca queda recortado por contenedores con overflow (tablas, modales)
   y se abre hacia arriba cuando no hay espacio abajo. */
function posicionar() {
  const el = control.value
  if (!el) return
  const r = el.getBoundingClientRect()
  const espacioAbajo = window.innerHeight - r.bottom - 8
  const espacioArriba = r.top - 8
  const abrirArriba = espacioAbajo < 220 && espacioArriba > espacioAbajo
  const maxAlto = Math.max(140, Math.min(240, abrirArriba ? espacioArriba : espacioAbajo))
  const estilo = { left: `${r.left}px`, width: `${r.width}px`, maxHeight: `${maxAlto}px` }
  if (abrirArriba) estilo.bottom = `${window.innerHeight - r.top + 4}px`
  else estilo.top = `${r.bottom + 4}px`
  dropStyle.value = estilo
}

function abrir() {
  if (props.disabled) return
  open.value = true
  query.value = ''
  nextTick(posicionar)
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
function cerrarConFoco() {
  setTimeout(() => {
    if (!open.value) return
    open.value = false
    query.value = selected.value ? selected.value.label : ''
  }, 140)
}
function onKeydown(e) {
  if (e.key === 'Escape') open.value = false
}

function onDocMousedown(e) {
  if (!open.value) return
  if (root.value?.contains(e.target) || drop.value?.contains(e.target)) return
  open.value = false
  query.value = selected.value ? selected.value.label : ''
}
function onReposicionar() { if (open.value) posicionar() }

watch(open, (o) => {
  if (o) {
    window.addEventListener('resize', onReposicionar)
    window.addEventListener('scroll', onReposicionar, true)
  } else {
    window.removeEventListener('resize', onReposicionar)
    window.removeEventListener('scroll', onReposicionar, true)
  }
})
document.addEventListener('mousedown', onDocMousedown, true)
onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocMousedown, true)
  window.removeEventListener('resize', onReposicionar)
  window.removeEventListener('scroll', onReposicionar, true)
})
</script>

<template>
  <div class="ss" ref="root">
    <div class="ss-control" :class="{ open, disabled }" ref="control">
      <input
        class="ss-input"
        :value="query"
        :placeholder="placeholder"
        :disabled="disabled"
        autocomplete="off"
        role="combobox"
        :aria-expanded="open"
        @input="query = $event.target.value; open = true"
        @focus="abrir"
        @blur="cerrarConFoco"
        @keydown="onKeydown"
      />
      <button v-if="clearable && modelValue != null && !disabled" type="button" class="ss-clear" @mousedown.prevent="clear" aria-label="Limpiar">
        <AppIcon name="close" :size="14" />
      </button>
      <AppIcon name="chevron" :size="16" class="ss-chev" />
    </div>
    <teleport to="body">
      <div
        v-if="open && !disabled"
        class="ss-drop"
        ref="drop"
        :style="dropStyle"
      >
        <button
          v-for="o in filtered"
          :key="o.value"
          type="button"
          class="ss-opt"
          :class="{ active: o.value === modelValue }"
          @mousedown.prevent="choose(o)"
        >
          <span class="ss-opt-label">{{ o.label }}</span>
          <small v-if="o.sub" class="ss-opt-sub">{{ o.sub }}</small>
        </button>
        <p v-if="!filtered.length" class="ss-empty">Sin coincidencias.</p>
      </div>
    </teleport>
  </div>
</template>

<style scoped>
.ss { position: relative; width: 100%; min-width: 0; }
.ss-control {
  display: flex; align-items: center; gap: .35rem;
  min-width: 0;
  border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm);
  background: #fff; padding: 0 .5rem;
}
.ss-control.open { border-color: var(--acr-azul); box-shadow: 0 0 0 3px rgba(33, 96, 173, .15); }
.ss-control.disabled { background: #F4F8FD; opacity: .8; }
.ss-input {
  flex: 1; min-width: 0; border: none; outline: none; background: transparent;
  padding: .55rem .25rem; font-size: .9rem; font-family: inherit; color: var(--acr-texto);
}
.ss-chev { color: var(--acr-texto-suave); flex: none; transform: rotate(0deg); transition: transform .15s; }
.ss-control.open .ss-chev { transform: rotate(180deg); }
.ss-clear { background: none; border: none; cursor: pointer; color: var(--acr-texto-suave); display: grid; place-items: center; flex: none; padding: 0; }
@media (max-width: 700px) { .ss-input { font-size: 1rem; } }
</style>

<style>
/* Global (el dropdown vive en <body> por el teleport) */
.ss-drop {
  position: fixed; z-index: 120;
  background: #fff; border: 1px solid #D6E2F2; border-radius: 7px;
  box-shadow: 0 1px 2px rgba(27, 39, 51, .06), 0 6px 18px rgba(27, 39, 51, .06);
  overflow-y: auto; padding: .25rem;
}
.ss-drop .ss-opt {
  display: block; width: 100%; text-align: left; border: none; background: none;
  padding: .5rem .6rem; border-radius: 6px; cursor: pointer; font-size: .88rem; color: #1B2733;
  font-family: inherit;
}
.ss-drop .ss-opt:hover { background: #EAF1FB; }
.ss-drop .ss-opt.active { background: #EAF1FB; color: #1A4E8C; font-weight: 600; }
.ss-drop .ss-opt-label { display: block; }
.ss-drop .ss-opt-sub { display: block; color: #5B6B7B; font-size: .76rem; margin-top: 1px; }
.ss-drop .ss-empty { margin: 0; padding: .5rem .6rem; color: #5B6B7B; font-size: .82rem; }
</style>
