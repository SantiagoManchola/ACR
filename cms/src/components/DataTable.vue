<script setup>
import AppIcon from './AppIcon.vue'
import { fmtNum } from '../utils/format'
import { computed, nextTick, onMounted, ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, align?, num?, sortValue? }]
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Sin registros.' },
  error: { type: String, default: '' },
  pageSize: { type: Number, default: 10 },
})

const page = ref(1)
const sortKey = ref('')
const sortDir = ref('asc') // asc | desc

/* Anchos congelados: al ordenar o paginar cambia el contenido visible y con
   table-layout auto el navegador recalcula anchos (salto visual). Se miden una
   vez, se guardan como porcentajes y la tabla pasa a table-layout fixed. */
const tablaEl = ref(null)
const colWidths = ref([])
const anchosFijos = ref(false)

async function congelarAnchos(intento = 0) {
  await nextTick()
  const el = tablaEl.value
  if (!el) return
  const ths = el.querySelectorAll('thead th')
  const total = el.offsetWidth
  if (!ths.length || total <= 0) {
    if (intento < 5) setTimeout(() => congelarAnchos(intento + 1), 120)
    return
  }
  colWidths.value = Array.from(ths).map((th) => {
    const w = th.offsetWidth
    return Number(Math.max(4, (w / total) * 100).toFixed(3))
  })
  anchosFijos.value = true
}

function descongelar() { anchosFijos.value = false; colWidths.value = [] }

watch(() => props.columns, () => { descongelar() })
watch(
  [() => props.rows, () => props.loading],
  () => {
    if (!props.loading && props.rows.length && !anchosFijos.value) congelarAnchos()
  },
  { deep: false }
)
onMounted(() => { if (props.rows.length && !props.loading) congelarAnchos() })

/* Valor usado para ordenar: col.sortValue(row) si existe, si no row[col.key] */
function valorOrden(row, col) {
  if (typeof col.sortValue === 'function') return col.sortValue(row)
  return row[col.key]
}

function comparar(a, b) {
  // Nulos/inválidos siempre al final
  const va = a === null || a === undefined || a === ''
  const vb = b === null || b === undefined || b === ''
  if (va && vb) return 0
  if (va) return 1
  if (vb) return -1
  // Números (o strings numéricos) primero
  const na = typeof a === 'number' ? a : Number(String(a).replace(',', ''))
  const nb = typeof b === 'number' ? b : Number(String(b).replace(',', ''))
  if (!Number.isNaN(na) && !Number.isNaN(nb)) return na - nb
  return String(a).localeCompare(String(b), 'es', { numeric: true, sensitivity: 'base' })
}

const ordenadas = computed(() => {
  if (!sortKey.value) return props.rows
  const col = props.columns.find((c) => c.key === sortKey.value)
  if (!col) return props.rows
  const lista = props.rows.slice()
  lista.sort((ra, rb) => {
    const r = comparar(valorOrden(ra, col), valorOrden(rb, col))
    return sortDir.value === 'asc' ? r : -r
  })
  return lista
})

function ordenarPor(col) {
  if (sortKey.value === col.key) {
    if (sortDir.value === 'asc') { sortDir.value = 'desc'; return }
    sortKey.value = ''; sortDir.value = 'asc'; return // tercer clic: sin orden
  }
  sortKey.value = col.key
  sortDir.value = 'asc'
}

function flecha(col) {
  if (sortKey.value !== col.key) return ''
  return sortDir.value === 'asc' ? '▲' : '▼'
}

const totalPages = computed(() => Math.max(1, Math.ceil(ordenadas.value.length / props.pageSize)))
const paginated = computed(() =>
  ordenadas.value.slice((page.value - 1) * props.pageSize, page.value * props.pageSize)
)
const rango = computed(() => {
  if (!ordenadas.value.length) return '0'
  const ini = (page.value - 1) * props.pageSize + 1
  const fin = Math.min(page.value * props.pageSize, ordenadas.value.length)
  return `${ini}–${fin} de ${ordenadas.value.length}`
})

watch(() => props.rows, () => { if (page.value > totalPages.value) page.value = 1 })
watch(totalPages, (t) => { if (page.value > t) page.value = t })
watch(sortKey, () => { page.value = 1 })
watch(sortDir, () => { page.value = 1 })

function goto(p) { page.value = Math.min(Math.max(1, p), totalPages.value) }
</script>

<template>
  <div class="data-table">
    <div v-if="error" class="alert alert-bad" style="margin-bottom:.8rem">
      <span>{{ error }}</span>
    </div>

    <div v-if="loading" class="state-block">
      <div class="spinner"></div>
      <p>Cargando…</p>
    </div>

    <div v-else-if="!rows.length" class="state-block">
      <AppIcon name="search" :size="28" />
      <p style="margin-top:.4rem">{{ emptyText }}</p>
    </div>

    <div v-else class="table-wrap">
      <table class="table" :class="{ 'table-fixed': anchosFijos }" ref="tablaEl">
        <colgroup v-if="anchosFijos">
          <col v-for="(w, i) in colWidths" :key="'w' + i" :style="{ width: w + '%' }" />
        </colgroup>
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :class="{ num: col.align === 'right', sortable: col.sortable !== false }"
              :title="col.sortable === false ? '' : 'Clic para ordenar'"
              @click="col.sortable !== false && ordenarPor(col)"
            >
              <span class="th-content">
                {{ col.label }}
                <span
                  v-if="col.sortable !== false"
                  class="sort-arrow"
                  :class="{ 'is-hidden': !flecha(col) }"
                  aria-hidden="true"
                >{{ flecha(col) || '▲' }}</span>
              </span>
            </th>
            <th v-if="$slots['row-actions']" class="num">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, i) in paginated" :key="row.id ?? i">
            <td v-for="col in columns" :key="col.key" :class="{ num: col.align === 'right' }">
              <slot name="cell" :row="row" :col="col">
                {{ col.num ? fmtNum(row[col.key]) : (row[col.key] ?? '—') }}
              </slot>
            </td>
            <td v-if="$slots['row-actions']" class="row-actions">
              <slot name="row-actions" :row="row" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && rows.length" class="table-pagination">
      <span class="muted">{{ rango }}</span>
      <div class="pager">
        <button class="btn btn-ghost btn-sm" :disabled="page <= 1" @click="goto(page - 1)">
          <AppIcon name="chevronLeft" :size="14" /> Anterior
        </button>
        <span class="pager-num">Página {{ page }} / {{ totalPages }}</span>
        <button class="btn btn-ghost btn-sm" :disabled="page >= totalPages" @click="goto(page + 1)">
          Siguiente <AppIcon name="chevronRight" :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.table thead th.sortable { cursor: pointer; user-select: none; white-space: nowrap; }
.table thead th.sortable:hover { color: var(--acr-azul); }
.th-content { display: inline-flex; align-items: center; gap: .3rem; }
/* Espacio del indicador reservado siempre: el ancho de la columna no salta al ordenar */
.sort-arrow {
  display: inline-block; width: .75em; text-align: center;
  font-size: .62rem; color: var(--acr-azul); line-height: 1;
}
.sort-arrow.is-hidden { visibility: hidden; }
.table thead th.num .th-content { flex-direction: row-reverse; }
/* Una vez medidos, los anchos quedan fijos: ordenar/paginar no los mueve */
.table.table-fixed { table-layout: fixed; }
.table.table-fixed td, .table.table-fixed th { overflow: hidden; text-overflow: ellipsis; }
</style>
