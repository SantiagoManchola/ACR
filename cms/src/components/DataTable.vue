<script setup>
import AppIcon from './AppIcon.vue'
import { fmtNum } from '../utils/format'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  columns: { type: Array, required: true }, // [{ key, label, align?, num?, sortValue?, hideOnCard?, cardTitle?, wide? }]
  rows: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: 'Sin registros.' },
  error: { type: String, default: '' },
  pageSize: { type: Number, default: 10 },
})

/* Mobile: en pantallas angostas se muestra lista de cards en vez de tabla. */
const bpCard = 700
const mq = typeof window !== 'undefined' ? window.matchMedia(`(max-width: ${bpCard}px)`) : null
const esMovil = ref(mq ? mq.matches : false)
function onMq(e) { esMovil.value = e.matches }
onMounted(() => { mq?.addEventListener('change', onMq) })
onBeforeUnmount(() => { mq?.removeEventListener('change', onMq) })

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
  if (esMovil.value) return
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
watch(esMovil, (movil) => {
  if (!movil && props.rows.length && !props.loading && !anchosFijos.value) congelarAnchos()
})

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

/* ---- Vista de cards (mobile) ---- */
const colsCard = computed(() => props.columns.filter((c) => !c.hideOnCard))
const colTitulo = computed(() => colsCard.value.find((c) => c.cardTitle) || colsCard.value[0] || null)
const colsCuerpo = computed(() => colsCard.value.filter((c) => c !== colTitulo.value))
const colsOrdenables = computed(() => props.columns.filter((c) => c.sortable !== false))

function cambiarOrdenMovil(key) {
  if (!key) { sortKey.value = ''; sortDir.value = 'asc'; return }
  sortKey.value = key
  sortDir.value = 'asc'
}
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

    <div v-else-if="esMovil" class="card-list">
      <div v-if="colsOrdenables.length" class="card-sort">
        <AppIcon name="sort" :size="16" class="card-sort-icon" />
        <select
          class="select card-sort-select"
          :value="sortKey"
          aria-label="Ordenar por"
          @change="cambiarOrdenMovil($event.target.value)"
        >
          <option value="">Sin ordenar</option>
          <option v-for="col in colsOrdenables" :key="col.key" :value="col.key">{{ col.label }}</option>
        </select>
        <button
          type="button"
          class="card-sort-dir"
          :disabled="!sortKey"
          :title="sortDir === 'asc' ? 'Ascendente' : 'Descendente'"
          :aria-label="sortDir === 'asc' ? 'Orden ascendente' : 'Orden descendente'"
          @click="sortDir = sortDir === 'asc' ? 'desc' : 'asc'"
        >
          <AppIcon :name="sortDir === 'asc' ? 'arrowUp' : 'arrowDown'" :size="15" />
        </button>
      </div>

      <article v-for="(row, i) in paginated" :key="row.id ?? i" class="card-row">
        <header v-if="colTitulo" class="card-row-head">
          <slot name="cell" :row="row" :col="colTitulo">
            <strong>{{ colTitulo.num ? fmtNum(row[colTitulo.key]) : (row[colTitulo.key] ?? '—') }}</strong>
          </slot>
        </header>
        <div class="card-row-body">
          <div v-for="col in colsCuerpo" :key="col.key" class="card-field" :class="{ wide: col.wide }">
            <span class="k">{{ col.label }}</span>
            <span class="v" :class="{ num: col.align === 'right' }">
              <slot name="cell" :row="row" :col="col">
                {{ col.num ? fmtNum(row[col.key]) : (row[col.key] ?? '—') }}
              </slot>
            </span>
          </div>
        </div>
        <footer v-if="$slots['row-actions']" class="card-row-actions">
          <slot name="row-actions" :row="row" />
        </footer>
      </article>
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

/* ----------------------------- Vista de cards (mobile) ----------------------------- */
.card-list { display: flex; flex-direction: column; gap: .6rem; }
.card-sort {
  display: flex; align-items: center; gap: .25rem;
  background: var(--acr-tarjeta); border: 1px solid var(--acr-borde);
  border-radius: var(--acr-radio); padding: .3rem .35rem .3rem .6rem;
  box-shadow: var(--acr-sombra-sm);
}
.card-sort-icon { color: var(--acr-azul); flex: none; }
.card-sort-select {
  flex: 1; min-width: 0; border: none; background-color: transparent; box-shadow: none;
  padding: 0 1.6rem 0 .4rem; font-size: .9rem; height: 2.1rem; line-height: normal;
  text-overflow: ellipsis; white-space: nowrap; overflow: hidden;
}
.card-sort-select:hover, .card-sort-select:focus { border: none; background-color: transparent; box-shadow: none; }
.card-sort-dir {
  flex: none; width: 2rem; height: 2rem; display: grid; place-items: center;
  border: 1px solid var(--acr-borde); border-radius: var(--acr-radio-sm);
  background: #fff; color: var(--acr-azul); cursor: pointer;
  transition: background .15s, border-color .15s, opacity .15s;
}
.card-sort-dir:disabled { opacity: .4; cursor: not-allowed; }
.card-sort-dir:not(:disabled):active { background: var(--acr-azul-50); border-color: var(--acr-azul); }
.card-row {
  background: var(--acr-tarjeta); border: 1px solid var(--acr-borde);
  border-radius: var(--acr-radio); box-shadow: var(--acr-sombra-sm);
  padding: .75rem .85rem;
}
.card-row-head {
  font-size: .95rem; color: var(--acr-texto);
  padding-bottom: .45rem; margin-bottom: .5rem;
  border-bottom: 1px solid #EEF3FA;
}
.card-row-body {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: .45rem .9rem;
}
.card-field { min-width: 0; }
.card-field.wide { grid-column: 1 / -1; }
.card-field .k {
  display: block; font-size: .68rem; text-transform: uppercase; letter-spacing: .03em;
  color: var(--acr-texto-suave); margin-bottom: .05rem;
}
.card-field .v { display: block; font-size: .86rem; overflow-wrap: anywhere; }
.card-field .v.num { font-variant-numeric: tabular-nums; }
.card-row-actions {
  display: flex; gap: .35rem; justify-content: flex-end; flex-wrap: wrap;
  margin-top: .6rem; padding-top: .55rem; border-top: 1px solid #EEF3FA;
}
</style>
