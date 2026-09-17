<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useInventarioStore } from '../stores/inventario'
import { useAuthStore } from '../stores/auth'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import BaseInput from '../components/BaseInput.vue'
import client, { apiError, descargarReporte } from '../api/http'
import { fmtNum, hoyColombia, formatoOptions } from '../utils/format'
import { debounce } from '../utils/debounce'
import { useBusy } from '../utils/async'

const inv = useInventarioStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

/* Roles: el CRUD de ubicaciones es SOLO admin; el administrativo SOLO ve
   inventario de la Oficina (el backend fuerza ese alcance; aquí se refleja
   en los filtros bloqueados). */
const esAdmin = computed(() => auth.rol === 'admin')
const esAdministrativo = computed(() => auth.rol === 'administrativo')
const oficinaUbi = computed(() => {
  const us = inv.ubicaciones || []
  // Coincidencia exacta primero: "Oficina" antes que "Nueva oficina".
  return us.find((u) => (u.nombre || '').toLowerCase() === 'oficina')
    || us.find((u) => /oficina/i.test(u.nombre || '')) || null
})
function forzarOficina() {
  const id = oficinaUbi.value ? oficinaUbi.value.id : ''
  filtros.value.ubicacion_id = id
  filtrosMov.value.ubicacion_id = id
  filtrosTras.value.origen_id = id
  filtrosTras.value.destino_id = id
}

const tab = ref('elementos')
/* Sincronía pestaña ↔ URL: /inventario/elementos, /inventario/categorias, …
   La pestaña es compartible y el navegador la conserva con back/forward. */
const TABS_VALIDOS = ['elementos', 'categorias', 'ubicaciones', 'traslados', 'movimientos', 'alertas']
watch(() => route.params.tab, (t) => {
  if (t === undefined) return // la ruta base solo existe como redirect
  if (!TABS_VALIDOS.includes(t)) { router.replace({ name: 'inventario', params: { tab: tab.value } }); return }
  if (t !== tab.value) tab.value = t
}, { immediate: true })
function setTab(t) {
  tab.value = t
  router.replace({ name: 'inventario', params: { tab: t } })
}
const showForm = ref(false)
const showMov = ref(false)
const showCat = ref(false)
const showUbi = ref(false)
const editing = ref(null)
const movTipo = ref('entrada')
const movElem = ref(null)
const formError = ref('')
const movError = ref('')
const catError = ref('')
const ubiError = ref('')
const saving = ref(false)
/* Cargas de botones asíncronos: deshabilitados hasta resolver la petición */
const { busy: repBusy, run: repRun } = useBusy()
const { busy: refrescando, run: refRun } = useBusy()
const { busy: accionBusy, run: accionRun } = useBusy()

/* Reportes */
const formatoReporte = ref('csv')
const repError = ref('')
async function generarReporte(tipo) {
  repError.value = ''
  const params = { tipo, formato: formatoReporte.value }
  if (tipo === 'elementos') {
    if (filtros.value.nombre) params.nombre = filtros.value.nombre
    if (filtros.value.categoria_id) params.categoria_id = filtros.value.categoria_id
    if (filtros.value.ubicacion_id) params.ubicacion_id = filtros.value.ubicacion_id
  }
  try {
    await descargarReporte('/reportes/inventario', params, `reporte_${tipo}`)
  } catch (e) {
    repError.value = apiError(e)
  }
}

/* Filtros de elementos */
const filtros = ref({ nombre: '', categoria_id: '', ubicacion_id: '' })
/* Página y orden de cada tabla (paginación y orden server-side) */
const pageElem = ref(1)
const pageMov = ref(1)
const pageTras = ref(1)
const ordenElem = ref(''); const dirElem = ref('asc')
const ordenMov = ref(''); const dirMov = ref('desc')
const ordenTras = ref(''); const dirTras = ref('desc')
function aplicarFiltros() {
  const f = {}
  if (filtros.value.nombre) f.nombre = filtros.value.nombre
  if (filtros.value.categoria_id) f.categoria_id = filtros.value.categoria_id
  if (filtros.value.ubicacion_id) f.ubicacion_id = filtros.value.ubicacion_id
  return f
}
function filtrar() { inv.loadElementos(aplicarFiltros(), pageElem.value, ordenElem.value, dirElem.value) }

/* Filtros de traslados */
/* Filtros de traslados (fechas por defecto: hoy en Colombia) */
const filtrosTras = ref({ elemento_id: '', origen_id: '', destino_id: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function aplicarFiltrosTras() {
  const f = {}
  if (filtrosTras.value.elemento_id) f.elemento_id = filtrosTras.value.elemento_id
  if (filtrosTras.value.origen_id) f.ubicacion_origen_id = filtrosTras.value.origen_id
  if (filtrosTras.value.destino_id) f.ubicacion_destino_id = filtrosTras.value.destino_id
  if (filtrosTras.value.fecha_inicio) f.fecha_inicio = filtrosTras.value.fecha_inicio
  if (filtrosTras.value.fecha_fin) f.fecha_fin = filtrosTras.value.fecha_fin
  return f
}
function filtrarTras() { inv.loadTraslados(aplicarFiltrosTras(), pageTras.value, ordenTras.value, dirTras.value) }

/* Filtros de movimientos (fechas por defecto: hoy en Colombia) */
const filtrosMov = ref({ elemento_id: '', ubicacion_id: '', tipo: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function aplicarFiltrosMov() {
  const f = {}
  if (filtrosMov.value.elemento_id) f.elemento_id = filtrosMov.value.elemento_id
  if (filtrosMov.value.ubicacion_id) f.ubicacion_id = filtrosMov.value.ubicacion_id
  if (filtrosMov.value.tipo) f.tipo = filtrosMov.value.tipo
  if (filtrosMov.value.fecha_inicio) f.fecha_inicio = filtrosMov.value.fecha_inicio
  if (filtrosMov.value.fecha_fin) f.fecha_fin = filtrosMov.value.fecha_fin
  return f
}
function filtrarMov() { inv.loadMovimientos(aplicarFiltrosMov(), pageMov.value, ordenMov.value, dirMov.value) }

/* Auto-búsqueda con debounce al cambiar cualquier filtro (vuelve a la página 1) */
watch(filtros, debounce(() => { pageElem.value = 1; filtrar() }, 350), { deep: true })
watch(filtrosTras, debounce(() => { pageTras.value = 1; filtrarTras() }, 350), { deep: true })
watch(filtrosMov, debounce(() => { pageMov.value = 1; filtrarMov() }, 350), { deep: true })
function irPaginaElem(p) { pageElem.value = p; filtrar() }
function irPaginaTras(p) { pageTras.value = p; inv.loadTraslados(aplicarFiltrosTras(), p, ordenTras.value, dirTras.value) }
function irPaginaMov(p) { pageMov.value = p; inv.loadMovimientos(aplicarFiltrosMov(), p, ordenMov.value, dirMov.value) }
function ordenarElem({ key, dir }) { ordenElem.value = key; dirElem.value = dir; pageElem.value = 1; filtrar() }
function ordenarMov({ key, dir }) { ordenMov.value = key; dirMov.value = dir; pageMov.value = 1; inv.loadMovimientos(aplicarFiltrosMov(), 1, key, dir) }
function ordenarTras({ key, dir }) { ordenTras.value = key; dirTras.value = dir; pageTras.value = 1; inv.loadTraslados(aplicarFiltrosTras(), 1, key, dir) }

const movTipoOptions = [
  { value: 'entrada', label: 'Entrada' },
  { value: 'salida', label: 'Salida' },
]
const catTipoOptions = [
  { value: 'equipo', label: 'Equipo' },
  { value: 'herramienta', label: 'Herramienta' },
  { value: 'laboratorio', label: 'Laboratorio' },
  { value: 'accesorio', label: 'Accesorio' },
  { value: 'insumo', label: 'Insumo' },
]

const catOptions = computed(() => inv.categorias.map((c) => ({ value: c.id, label: `${c.nombre} (${c.tipo})` })))
const ubiOptions = computed(() => inv.ubicaciones.map((u) => ({ value: u.id, label: u.nombre })))
const ubicMap = computed(() => Object.fromEntries(inv.ubicaciones.map((u) => [u.id, u.nombre])))
const catMap = computed(() => Object.fromEntries(inv.categorias.map((c) => [c.id, c.nombre])))
/* Catálogo ligero para selects/mapeos (no depende de la página de la tabla) */
const opcionesMap = computed(() => Object.fromEntries(inv.opciones.map((e) => [e.id, e])))
const elementoOptions = computed(() => inv.opciones.map((e) => {
  const stock = e.stock && e.stock.length
    ? e.stock.map((s) => `${ubicMap.value[s.ubicacion_id] || '—'}: ${fmtNum(s.cantidad)}`).join(', ')
    : 'sin stock'
  return { value: e.id, label: `${e.nombre} — ${stock}` }
}))

/* Categorías */
const emptyCat = () => ({ nombre: '', tipo: 'equipo', descripcion: '' })
const catForm = ref(emptyCat())
const catCols = [
  { key: 'nombre', label: 'Nombre', cardTitle: true },
  { key: 'tipo', label: 'Tipo' },
  { key: 'descripcion', label: 'Descripción', wide: true },
]
function openNewCat() { catForm.value = emptyCat(); catError.value = ''; showCat.value = true }
async function saveCat() {
  catError.value = ''
  if (!catForm.value.nombre) { catError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try { await inv.createCategoria({ ...catForm.value }); showCat.value = false; await inv.loadCategorias() }
  catch (e) { catError.value = apiError(e) } finally { saving.value = false }
}

/* Ubicaciones */
const emptyUbi = () => ({ nombre: '', descripcion: '' })
const ubiForm = ref(emptyUbi())
const ubiCols = [
  { key: 'nombre', label: 'Nombre', cardTitle: true },
  { key: 'descripcion', label: 'Descripción', wide: true },
]
const editingUbi = ref(null)
function openNewUbi() { editingUbi.value = null; ubiForm.value = emptyUbi(); ubiError.value = ''; showUbi.value = true }
function openEditUbi(r) { editingUbi.value = r; ubiForm.value = { ...r }; ubiError.value = ''; showUbi.value = true }
async function saveUbi() {
  ubiError.value = ''
  if (!ubiForm.value.nombre) { ubiError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try {
    if (editingUbi.value) await inv.updateUbicacion(editingUbi.value.id, { ...ubiForm.value })
    else await inv.createUbicacion({ ...ubiForm.value })
    showUbi.value = false; await inv.loadUbicaciones()
  } catch (e) { ubiError.value = apiError(e) } finally { saving.value = false }
}

/* Resumen por ubicación (cuántos productos y cuántas unidades hay en cada lugar) */
const resumenUbi = computed(() => {
  const map = {}
  for (const u of inv.ubicaciones) map[u.id] = { nombre: u.nombre, productos: 0, unidades: 0 }
  for (const e of inv.opciones) {
    for (const s of (e.stock || [])) {
      if (map[s.ubicacion_id]) {
        map[s.ubicacion_id].productos += 1
        map[s.ubicacion_id].unidades += Number(s.cantidad) || 0
      }
    }
  }
  return Object.values(map).filter((r) => !esAdministrativo.value || (oficinaUbi.value && r.nombre === oficinaUbi.value.nombre))
})

/* Confirmación de acciones destructivas */
const confirmShow = ref(false)
const confirmMsg = ref('')
const pendingDel = ref(null)
function askDelElem(r) {
  pendingDel.value = r
  confirmMsg.value = `¿Inactivar el elemento «${r.nombre}»?`
  confirmShow.value = true
}
async function doDelElem() {
  const r = pendingDel.value
  if (!r) return
  await accionRun(async () => {
    await inv.deleteElemento(r.id)
    await Promise.all([inv.loadElementos(aplicarFiltros(), pageElem.value), inv.loadOpciones()])
    confirmShow.value = false
    pendingDel.value = null
  })
}
async function reactivarElem(r) {
  await accionRun(async () => {
    await inv.updateElemento(r.id, { estado: 'activo' })
    await Promise.all([inv.loadElementos(aplicarFiltros(), pageElem.value), inv.loadOpciones()])
  })
}

function refreshInv() {
  return Promise.all([
    inv.loadCategorias(), inv.loadUbicaciones(), inv.loadOpciones(),
    filtrar(), filtrarTras(), filtrarMov(), inv.loadAlertas(),
  ])
}

const emptyForm = () => ({
  nombre: '', categoria_id: null, unidad: '', proveedor: '', valor: '', minimo: '',
  observaciones: '', ubicacion_inicial: null, cantidad_inicial: '',
})
const form = ref(emptyForm())
const movForm = ref({ ubicacion_id: null, cantidad: '', motivo: '', observaciones: '', fecha: hoyColombia() })

const elementosCols = [
  { key: 'nombre', label: 'Elemento', cardTitle: true },
  { key: 'categoria', label: 'Categoría', sortValue: (r) => catMap.value[r.categoria_id] || '' },
  { key: 'ubicaciones', label: 'Ubicaciones', sortable: false, wide: true },
  /* La cantidad total se calcula en la API con todos los stocks: no es
     ordenable server-side (se muestra sin orden) */
  { key: 'cantidad', label: 'Cant. total', align: 'right', num: true, sortable: false },
  { key: 'unidad', label: 'Unidad' },
  { key: 'minimo', label: 'Mín.', align: 'right' },
]
const movCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'elemento', label: 'Elemento', cardTitle: true, sortValue: (r) => opcionesMap.value[r.elemento_id]?.nombre || '' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'motivo', label: 'Motivo', wide: true },
]
const alertCols = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'nombre', label: 'Elemento', cardTitle: true },
  { key: 'categoria', label: 'Categoría' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'minimo', label: 'Mínimo', align: 'right', num: true },
]
const ubiColsFinal = ubiCols

function openNew() { editing.value = null; form.value = emptyForm(); formError.value = ''; showForm.value = true }
function openEdit(row) {
  editing.value = row
  form.value = {
    nombre: row.nombre, categoria_id: row.categoria_id, unidad: row.unidad || '',
    proveedor: row.proveedor || '', valor: row.valor ?? '', minimo: row.minimo ?? '',
    observaciones: row.observaciones || '', ubicacion_inicial: null, cantidad_inicial: '',
  }
  formError.value = ''; showForm.value = true
}
function openMov(row, tipo) {
  movElem.value = row
  movTipo.value = tipo
  const primera = (row.stock && row.stock[0] && row.stock[0].ubicacion_id) || null
  movForm.value = { ubicacion_id: primera, cantidad: '', motivo: '', observaciones: '', fecha: hoyColombia() }
  movError.value = ''
  showMov.value = true
}

async function saveElemento() {
  formError.value = ''
  if (!form.value.nombre || !form.value.categoria_id) { formError.value = 'Nombre y categoría son obligatorios.'; return }
  saving.value = true
  try {
    const payload = {
      nombre: form.value.nombre,
      categoria_id: Number(form.value.categoria_id),
      unidad: form.value.unidad || null,
      proveedor: form.value.proveedor || null,
      valor: form.value.valor === '' ? null : Number(form.value.valor),
      minimo: form.value.minimo === '' ? null : Number(form.value.minimo),
      observaciones: form.value.observaciones || null,
    }
    if (!editing.value) {
      payload.ubicacion_id = form.value.ubicacion_inicial ? Number(form.value.ubicacion_inicial) : null
      payload.cantidad_inicial = form.value.cantidad_inicial === '' ? null : Number(form.value.cantidad_inicial)
    }
    if (editing.value) await inv.updateElemento(editing.value.id, payload)
    else await inv.createElemento(payload)
    showForm.value = false
    await Promise.all([inv.loadElementos(aplicarFiltros(), pageElem.value), inv.loadOpciones()])
  } catch (e) { formError.value = apiError(e) } finally { saving.value = false }
}

async function saveMov() {
  movError.value = ''
  if (!movForm.value.ubicacion_id) { movError.value = 'Seleccione la ubicación.'; return }
  if (!movForm.value.cantidad || Number(movForm.value.cantidad) <= 0) { movError.value = 'Ingrese una cantidad mayor a 0.'; return }
  saving.value = true
  try {
    await inv.registrarMovimiento(movElem.value.id, movTipo.value, {
      ubicacion_id: Number(movForm.value.ubicacion_id),
      cantidad: Number(movForm.value.cantidad),
      motivo: movForm.value.motivo,
      observaciones: movForm.value.observaciones,
      fecha: movForm.value.fecha,
    })
    showMov.value = false
    await Promise.all([
      inv.loadElementos(aplicarFiltros(), pageElem.value),
      inv.loadOpciones(),
      inv.loadMovimientos(aplicarFiltrosMov(), pageMov.value),
      inv.loadAlertas(),
    ])
  } catch (e) { movError.value = apiError(e) } finally { saving.value = false }
}

/* Traslados: mover el MISMO producto entre dos ubicaciones */
const showTras = ref(false)
const trasForm = ref({ elemento_id: null, ubicacion_origen_id: null, ubicacion_destino_id: null, cantidad: '', observaciones: '', fecha: hoyColombia() })
const trasError = ref('')
function openNewTras() {
  trasForm.value = { elemento_id: null, ubicacion_origen_id: null, ubicacion_destino_id: null, cantidad: '', observaciones: '', fecha: hoyColombia() }
  // El administrativo solo saca stock de la Oficina: origen predefinido.
  if (esAdministrativo.value && oficinaUbi.value) trasForm.value.ubicacion_origen_id = oficinaUbi.value.id
  trasError.value = ''; showTras.value = true
}
const trasUbicOrigenOptions = computed(() => {
  const e = opcionesMap.value[trasForm.value.elemento_id]
  if (!e || !e.stock) return []
  return e.stock.map((s) => ({ value: s.ubicacion_id, label: `${ubicMap.value[s.ubicacion_id] || '—'} (${fmtNum(s.cantidad)})` }))
})
const trasUbicDestinoOptions = computed(() => ubiOptions.value.filter((u) => u.value !== trasForm.value.ubicacion_origen_id))
async function saveTras() {
  trasError.value = ''
  if (!trasForm.value.elemento_id || !trasForm.value.ubicacion_origen_id || !trasForm.value.ubicacion_destino_id || !trasForm.value.cantidad || Number(trasForm.value.cantidad) <= 0) {
    trasError.value = 'Seleccione producto, origen, destino y una cantidad mayor a 0.'
    return
  }
  saving.value = true
  try {
    await inv.createTraslado({
      elemento_id: Number(trasForm.value.elemento_id),
      ubicacion_origen_id: Number(trasForm.value.ubicacion_origen_id),
      ubicacion_destino_id: Number(trasForm.value.ubicacion_destino_id),
      cantidad: Number(trasForm.value.cantidad),
      observaciones: trasForm.value.observaciones || null,
      fecha: trasForm.value.fecha,
    })
    showTras.value = false
    await Promise.all([
      inv.loadElementos(aplicarFiltros(), pageElem.value),
      inv.loadOpciones(),
      inv.loadTraslados(aplicarFiltrosTras(), pageTras.value),
    ])
  } catch (e) { trasError.value = apiError(e) } finally { saving.value = false }
}

const trasladoCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'elemento', label: 'Producto', cardTitle: true, sortValue: (r) => r.elemento_nombre || opcionesMap.value[r.elemento_id]?.nombre || '' },
  { key: 'origen', label: 'Origen' },
  { key: 'destino', label: 'Destino' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'responsable', label: 'Responsable', sortValue: (r) => r.responsable_nombre || '' },
]
const elemMap = opcionesMap

/* Quitar el producto de una ubicación cuando su stock quedó en 0 */
async function removeStock(s) {
  if (!confirm(`¿Quitar "${editing.value?.nombre}" de la ubicación "${ubicMap.value[s.ubicacion_id] || '—'}"?`)) return
  try {
    await inv.deleteStock(s.id)
    await inv.loadOpciones()
    const actualizado = await inv.loadElemento(s.elemento_id)
    if (actualizado) editing.value = actualizado
  } catch (e) {
    alert(apiError(e))
  }
}

function badgeTone(tipo) { return tipo === 'entrada' ? 'badge-ok' : 'badge-warn' }

onMounted(() => {
  /* Cargas en paralelo desde el primer render (el backend fuerza el alcance
     Oficina para el administrativo; los filtros se rellenan al llegar las
     ubicaciones y el watch re-consulta una sola vez). Sin awaits previos:
     la tabla nunca arranca mostrando "Sin información". */
  filtrar()
  filtrarMov()
  filtrarTras()
  inv.loadOpciones()
  inv.loadAlertas()
  inv.loadCategorias()
  inv.loadUbicaciones().then(() => {
    if (esAdministrativo.value) forzarOficina()
  })
})

watch(() => tab.value, (t) => {
  if (t === 'ubicaciones') inv.loadUbicaciones()
  if (t === 'categorias') inv.loadCategorias()
  if (t === 'elementos') filtrar()
  if (t === 'alertas') inv.loadAlertas()
  if (t === 'traslados') filtrarTras()
  if (t === 'movimientos') filtrarMov()
})
</script>

<template>
  <div class="view-fit">
    <h1>Inventario</h1>
    <p class="muted">Productos, ubicaciones, traslados, movimientos y alertas de existencias.</p>
    <p v-if="esAdministrativo" class="muted">Viendo inventario de <strong>{{ oficinaUbi?.nombre || 'Oficina' }}</strong>: tu rol solo tiene alcance a esa ubicación.</p>

    <div class="tabs">
      <button :class="{ active: tab === 'elementos' }" @click="setTab('elementos')"><AppIcon name="package" />Elementos</button>
      <button :class="{ active: tab === 'categorias' }" @click="setTab('categorias')"><AppIcon name="tag" />Categorías</button>
      <button :class="{ active: tab === 'ubicaciones' }" @click="setTab('ubicaciones')"><AppIcon name="mapPin" />Ubicaciones</button>
      <button :class="{ active: tab === 'traslados' }" @click="setTab('traslados')"><AppIcon name="swap" />Traslados</button>
      <button :class="{ active: tab === 'movimientos' }" @click="setTab('movimientos')"><AppIcon name="refresh" />Movimientos</button>
      <button :class="{ active: tab === 'alertas' }" @click="setTab('alertas')">
        <AppIcon name="alert" />Alertas
        <span v-if="inv.alertas.length" class="badge badge-bad">{{ inv.alertas.length }}</span>
      </button>
    </div>

    <!-- ELEMENTOS -->
    <div v-if="tab === 'elementos'" class="tab-panel">
      <div class="filter-bar">
        <div class="field">
          <label>Nombre</label>
          <BaseInput v-model="filtros.nombre" placeholder="Buscar por nombre…" />
        </div>
        <div class="field">
          <label>Categoría</label>
          <SearchableSelect v-model="filtros.categoria_id" :options="catOptions" placeholder="Todas" clearable />
        </div>
        <div class="field">
          <label>Ubicación</label>
          <SearchableSelect v-model="filtros.ubicacion_id" :options="ubiOptions" placeholder="Todas" clearable :disabled="esAdministrativo" />
        </div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNew"><AppIcon name="plus" />Nuevo elemento</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refRun(refreshInv)"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable
        :columns="elementosCols" :rows="inv.elementos" :loading="inv.loading"
        :total="inv.elementosTotal" :page="pageElem" :page-size="20"
        :sort-by="ordenElem" :sort-dir="dirElem"
        empty-text="No hay elementos registrados."
        @update:page="irPaginaElem"
        @update:sort="ordenarElem"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'categoria'">{{ catMap[row.categoria_id] || '—' }}</span>
          <span v-else-if="col.key === 'ubicaciones'">
            <template v-if="row.stock && row.stock.length">
              <span v-for="s in row.stock" :key="s.id" class="chip">{{ ubicMap[s.ubicacion_id] || '—' }}: {{ fmtNum(s.cantidad) }}</span>
            </template>
            <span v-else class="muted">sin stock</span>
          </span>
          <span v-else-if="col.key === 'minimo'">
            <span class="badge" :class="(row.minimo != null && Number(row.cantidad) <= Number(row.minimo)) ? 'badge-bad' : 'badge-muted'">{{ fmtNum(row.minimo) }}</span>
          </span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEdit(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openMov(row, 'entrada')" title="Entrada"><AppIcon name="plus" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openMov(row, 'salida')" title="Salida"><AppIcon name="minus" :size="16" /></button>
          <button v-if="row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="askDelElem(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-else class="btn btn-ghost btn-sm" :disabled="accionBusy" @click="accionRun(() => reactivarElem(row))" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:140px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('elementos'))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
      <BaseAlert v-if="repError" type="bad" class="mt-1">{{ repError }}</BaseAlert>
    </div>

    <!-- CATEGORÍAS -->
    <div v-else-if="tab === 'categorias'" class="tab-panel">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewCat"><AppIcon name="plus" />Nueva categoría</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refRun(refreshInv)"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable :columns="catCols" :rows="inv.categorias" :loading="inv.loading" empty-text="Sin categorías registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo'" style="text-transform:capitalize">{{ row.tipo }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- UBICACIONES -->
    <div v-else-if="tab === 'ubicaciones'" class="tab-panel">
      <div class="toolbar">
        <button v-if="esAdmin" class="btn btn-primary" @click="openNewUbi"><AppIcon name="plus" />Nueva ubicación</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refRun(refreshInv)"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <div class="resumen-ubi" v-if="resumenUbi.length">
        <div class="resumen-card" v-for="r in resumenUbi" :key="r.nombre">
          <span class="resumen-nombre"><AppIcon name="mapPin" :size="14" />{{ r.nombre }}</span>
          <span class="resumen-dato">{{ r.productos }} {{ r.productos === 1 ? 'producto' : 'productos' }}</span>
          <span class="resumen-dato resumen-unidades">{{ fmtNum(r.unidades) }} uds.</span>
        </div>
      </div>
      <DataTable :columns="ubiColsFinal" :rows="inv.ubicaciones" :loading="inv.loading" empty-text="Sin ubicaciones registradas.">
        <template #row-actions="{ row }">
          <button v-if="esAdmin" class="btn btn-ghost btn-sm" @click="openEditUbi(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
        </template>
      </DataTable>
    </div>

    <!-- TRASLADOS -->
    <div v-else-if="tab === 'traslados'" class="tab-panel">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewTras"><AppIcon name="swap" />Nuevo traslado</button>
      </div>
      <div class="filter-bar">
        <div class="field">
          <label>Producto</label>
          <SearchableSelect v-model="filtrosTras.elemento_id" :options="elementoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field" v-if="!esAdministrativo">
          <label>Origen</label>
          <SearchableSelect v-model="filtrosTras.origen_id" :options="ubiOptions" placeholder="Todas" clearable />
        </div>
        <div class="field" v-if="!esAdministrativo">
          <label>Destino</label>
          <SearchableSelect v-model="filtrosTras.destino_id" :options="ubiOptions" placeholder="Todas" clearable />
        </div>
        <p v-else class="muted" style="align-self:end">Alcance: traslados donde participa {{ oficinaUbi?.nombre || 'Oficina' }} (los lugares se muestran solo como información).</p>
        <div class="field">
          <label>Desde</label>
          <BaseInput v-model="filtrosTras.fecha_inicio" type="date" />
        </div>
        <div class="field">
          <label>Hasta</label>
          <BaseInput v-model="filtrosTras.fecha_fin" type="date" />
        </div>
      </div>
      <DataTable
        :columns="trasladoCols" :rows="inv.traslados" :loading="inv.loading"
        :total="inv.trasladosTotal" :page="pageTras" :page-size="20"
        :sort-by="ordenTras" :sort-dir="dirTras"
        empty-text="Sin traslados registrados."
        @update:page="irPaginaTras"
        @update:sort="ordenarTras"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'elemento'">{{ row.elemento_nombre || elemMap[row.elemento_id]?.nombre || row.elemento_id }}</span>
          <span v-else-if="col.key === 'origen'">{{ row.ubicacion_origen || '—' }}</span>
          <span v-else-if="col.key === 'destino'">{{ row.ubicacion_destino || '—' }}</span>
          <span v-else-if="col.key === 'responsable'">{{ row.responsable_nombre || '—' }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- MOVIMIENTOS -->
    <div v-else-if="tab === 'movimientos'" class="tab-panel">
      <div class="filter-bar">
        <div class="field">
          <label>Elemento</label>
          <SearchableSelect v-model="filtrosMov.elemento_id" :options="elementoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field">
          <label>Ubicación</label>
          <SearchableSelect v-model="filtrosMov.ubicacion_id" :options="ubiOptions" placeholder="Todas" clearable :disabled="esAdministrativo" />
        </div>
        <div class="field">
          <label>Tipo</label>
          <SearchableSelect v-model="filtrosMov.tipo" :options="movTipoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field">
          <label>Desde</label>
          <BaseInput v-model="filtrosMov.fecha_inicio" type="date" />
        </div>
        <div class="field">
          <label>Hasta</label>
          <BaseInput v-model="filtrosMov.fecha_fin" type="date" />
        </div>
      </div>
      <DataTable
        :columns="movCols" :rows="inv.movimientos" :loading="inv.loading"
        :total="inv.movimientosTotal" :page="pageMov" :page-size="20"
        :sort-by="ordenMov" :sort-dir="dirMov"
        empty-text="Sin movimientos registrados."
        @update:page="irPaginaMov"
        @update:sort="ordenarMov"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'elemento'">{{ row.elemento_nombre || opcionesMap.value[row.elemento_id]?.nombre || row.elemento_id }}</span>
          <span v-else-if="col.key === 'ubicacion'">{{ row.ubicacion || '—' }}</span>
          <span v-else-if="col.key === 'tipo'"><span class="badge" :class="badgeTone(row.tipo)">{{ row.tipo }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- ALERTAS -->
    <div v-else class="tab-panel">
      <BaseAlert v-if="!inv.alertas.length" type="ok" class="mb-1">No hay elementos bajo el mínimo configurado.</BaseAlert>
      <DataTable v-else :columns="alertCols" :rows="inv.alertas" :loading="inv.loading" empty-text="Sin alertas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo'"><span class="badge badge-muted">{{ row.tipo }}</span></span>
          <span v-else-if="col.key === 'categoria'">{{ row.categoria }}</span>
          <span v-else-if="col.key === 'ubicacion'">{{ row.ubicacion || '—' }}</span>
          <span v-else-if="col.key === 'minimo'"><span class="badge badge-bad">{{ fmtNum(row.minimo) }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- FORM ELEMENTO -->
    <BaseModal v-model="showForm" :title="editing ? 'Editar elemento' : 'Nuevo elemento'">
      <BaseAlert v-if="formError" type="bad" class="mb-1">{{ formError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column: span 2">
          <label>Nombre *</label>
          <input class="input" v-model="form.nombre" />
        </div>
        <div class="field">
          <label>Categoría *</label>
          <SearchableSelect v-model="form.categoria_id" :options="catOptions" placeholder="Seleccione…" />
        </div>
        <div class="field">
          <label>Unidad</label>
          <input class="input" v-model="form.unidad" placeholder="Ej. unidad, caja, kg" />
        </div>
        <div class="field">
          <label>Proveedor</label>
          <input class="input" v-model="form.proveedor" />
        </div>
        <div class="field">
          <label>Valor unitario</label>
          <div style="display:flex; align-items:center; gap:.4rem">
            <span style="font-weight:600; color:var(--acr-texto)">$</span>
            <input class="input" type="number" step="0.01" placeholder="0" v-model="form.valor" style="flex:1" />
          </div>
        </div>
        <div class="field">
          <label>Mínimo (alerta)</label>
          <input class="input" type="number" step="0.01" placeholder="0" v-model="form.minimo" />
        </div>
        <template v-if="!editing">
          <div class="field">
            <label>Ubicación inicial</label>
            <SearchableSelect v-model="form.ubicacion_inicial" :options="ubiOptions" placeholder="Opcional" />
          </div>
          <div class="field">
            <label>Cantidad inicial</label>
            <input class="input" type="number" step="0.01" placeholder="0" v-model="form.cantidad_inicial" />
          </div>
        </template>
      </div>
      <div class="field">
        <label>Observaciones</label>
        <textarea class="textarea" v-model="form.observaciones"></textarea>
      </div>
      <div v-if="editing && editing.stock && editing.stock.length" class="field">
        <label>Existencias actuales por ubicación</label>
        <div class="stock-readonly">
          <span v-for="s in editing.stock" :key="s.id" class="chip-stock">
            <span>{{ ubicMap[s.ubicacion_id] || '—' }}: {{ fmtNum(s.cantidad) }}</span>
            <button v-if="Number(s.cantidad) === 0" class="chip-del" title="Quitar de esta ubicación" @click="removeStock(s)"><AppIcon name="trash" :size="14" /></button>
          </span>
        </div>
        <p class="muted sm">Puedes quitar el producto de una ubicación cuando su stock quedó en 0 (ya no se procesa allí).</p>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showForm = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveElemento">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- MOVIMIENTO -->
    <BaseModal v-model="showMov" :title="(movTipo === 'entrada' ? 'Registrar entrada' : 'Registrar salida') + ' · ' + (movElem?.nombre || '')">
      <BaseAlert v-if="movError" type="bad" class="mb-1">{{ movError }}</BaseAlert>
      <div class="field">
        <label>Ubicación *</label>
        <SearchableSelect v-model="movForm.ubicacion_id" :options="ubiOptions" placeholder="Seleccione ubicación…" />
      </div>
      <div class="field">
        <label>Cantidad *</label>
        <input class="input" type="number" step="0.01" placeholder="0" v-model="movForm.cantidad" />
      </div>
      <div class="field">
        <label>Motivo</label>
        <input class="input" v-model="movForm.motivo" :placeholder="movTipo === 'salida' ? 'Ej. instalación, mantenimiento' : 'Ej. compra, donación'" />
      </div>
      <div class="field">
        <label>Fecha</label>
        <BaseInput v-model="movForm.fecha" type="date" />
      </div>
      <div class="field">
        <label>Observaciones</label>
        <textarea class="textarea" v-model="movForm.observaciones"></textarea>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showMov = false">Cancelar</button>
        <button class="btn" :class="movTipo === 'entrada' ? 'btn-primary' : 'btn-ghost'" :disabled="saving" @click="saveMov">{{ saving ? 'Guardando…' : 'Registrar' }}</button>
      </template>
    </BaseModal>

    <!-- CATEGORÍA -->
    <BaseModal v-model="showCat" title="Nueva categoría">
      <BaseAlert v-if="catError" type="bad" class="mb-1">{{ catError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="catForm.nombre" /></div>
        <div class="field"><label>Tipo *</label>
          <SearchableSelect v-model="catForm.tipo" :options="catTipoOptions" placeholder="Tipo" />
        </div>
        <div class="field" style="grid-column:span 2"><label>Descripción</label><textarea class="textarea" v-model="catForm.descripcion" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showCat = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveCat">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- UBICACIÓN -->
    <BaseModal v-model="showUbi" :title="editingUbi ? 'Editar ubicación' : 'Nueva ubicación'">
      <BaseAlert v-if="ubiError" type="bad" class="mb-1">{{ ubiError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="ubiForm.nombre" placeholder="Ej. Oficina, Planta de tratamiento" /></div>
        <div class="field" style="grid-column:span 2"><label>Descripción</label><textarea class="textarea" v-model="ubiForm.descripcion" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showUbi = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveUbi">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- TRASLADO -->
    <BaseModal v-model="showTras" title="Registrar traslado">
      <BaseAlert v-if="trasError" type="bad" class="mb-1">{{ trasError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2">
          <label>Producto *</label>
          <SearchableSelect v-model="trasForm.elemento_id" :options="elementoOptions" placeholder="Seleccione el producto…" />
        </div>
        <div class="field" style="grid-column:span 2">
          <label>Ubicación de origen *</label>
          <SearchableSelect v-model="trasForm.ubicacion_origen_id" :options="trasUbicOrigenOptions" placeholder="De dónde sale" :disabled="esAdministrativo" />
        </div>
        <div class="field" style="grid-column:span 2">
          <label>Ubicación de destino *</label>
          <SearchableSelect v-model="trasForm.ubicacion_destino_id" :options="trasUbicDestinoOptions" placeholder="A dónde llega" />
        </div>
        <div class="field"><label>Cantidad *</label><input class="input" type="number" step="0.01" placeholder="0" v-model="trasForm.cantidad" /></div>
        <div class="field"><label>Fecha</label><BaseInput v-model="trasForm.fecha" type="date" /></div>
        <div class="field" style="grid-column:span 2"><label>Observaciones</label><textarea class="textarea" v-model="trasForm.observaciones" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showTras = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveTras">{{ saving ? 'Guardando…' : 'Registrar traslado' }}</button>
      </template>
    </BaseModal>

    <ConfirmModal v-model:show="confirmShow" title="Inactivar elemento" :message="confirmMsg" confirm-text="Sí, inactivar" danger :loading="accionBusy" @confirm="doDelElem" />
  </div>
</template>

<style scoped>
.chip {
  display: inline-block;
  background: var(--acr-azul-50);
  color: var(--acr-azul);
  border-radius: 999px;
  padding: .1rem .5rem;
  font-size: .75rem;
  margin: 0 .2rem .2rem 0;
}
.chip-stock {
  display: inline-flex;
  align-items: center;
  gap: .25rem;
  background: var(--acr-azul-50);
  color: var(--acr-azul);
  border-radius: 999px;
  padding: .1rem .35rem .1rem .6rem;
  font-size: .75rem;
  margin: 0 .2rem .2rem 0;
}
.chip-del {
  display: inline-flex;
  border: none;
  background: transparent;
  color: var(--acr-bad);
  cursor: pointer;
  padding: 0;
  border-radius: 50%;
  line-height: 1;
}
.chip-del:hover { background: rgba(184,54,54,.12); }
.stock-readonly { display: flex; flex-wrap: wrap; gap: .2rem; }
.muted.sm { font-size: .78rem; margin-top: .3rem; }
</style>
