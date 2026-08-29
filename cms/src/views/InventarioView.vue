<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useInventarioStore } from '../stores/inventario'
import { useAuthStore } from '../stores/auth'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import client, { apiError, descargarReporte } from '../api/http'
import { fmtNum } from '../utils/format'

const inv = useInventarioStore()
const auth = useAuthStore()

const tab = ref('elementos')
const showForm = ref(false)
const showMov = ref(false)
const showCat = ref(false)
const showQuimico = ref(false)
const editingQuimico = ref(null)
const showDosis = ref(false)
const editing = ref(null)
const movTipo = ref('entrada')
const movElem = ref(null)
const formError = ref('')
const movError = ref('')
const catError = ref('')
const quimicoError = ref('')
const dosisError = ref('')
const saving = ref(false)

/* Reportes */
const formatoReporte = ref('csv')
const repError = ref('')
async function generarReporte(tipo) {
  repError.value = ''
  const params = { tipo, formato: formatoReporte.value }
  if (tipo === 'elementos') {
    if (filtros.value.nombre) params.nombre = filtros.value.nombre
    if (filtros.value.categoria_id) params.categoria_id = filtros.value.categoria_id
  }
  try {
    await descargarReporte('/reportes/inventario', params, `reporte_${tipo}`)
  } catch (e) {
    repError.value = apiError(e)
  }
}

/* Filtros de elementos */
const filtros = ref({ nombre: '', categoria_id: '' })
function aplicarFiltros() {
  const f = {}
  if (filtros.value.nombre) f.nombre = filtros.value.nombre
  if (filtros.value.categoria_id) f.categoria_id = filtros.value.categoria_id
  return f
}
function filtrar() { inv.loadElementos(aplicarFiltros()) }
function limpiarFiltros() { filtros.value = { nombre: '', categoria_id: '' }; inv.loadElementos() }

const catOptions = computed(() => inv.categorias.map((c) => ({ value: c.id, label: `${c.nombre} (${c.tipo})` })))

/* Categorías */
const emptyCat = () => ({ nombre: '', tipo: 'equipo', descripcion: '' })
const catForm = ref(emptyCat())
const catCols = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'descripcion', label: 'Descripción' },
]
function openNewCat() { catForm.value = emptyCat(); catError.value = ''; showCat.value = true }
async function saveCat() {
  catError.value = ''
  if (!catForm.value.nombre) { catError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try { await inv.createCategoria({ ...catForm.value }); showCat.value = false; await inv.loadCategorias() }
  catch (e) { catError.value = apiError(e) } finally { saving.value = false }
}

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
  confirmShow.value = false
  if (!r) return
  await inv.deleteElemento(r.id)
  await inv.loadElementos()
  pendingDel.value = null
}
async function reactivarElem(r) {
  await inv.updateElemento(r.id, { estado: 'activo' })
  await inv.loadElementos()
}

function refreshInv() { return Promise.all([inv.loadCategorias(), inv.loadElementos(), inv.loadMovimientos(), inv.loadAlertas(), inv.loadQuimicos(), inv.loadDosificacionesInv()]) }

/* Químicos / Dosificaciones (los químicos son insumos dentro del inventario) */
const insumoCatOptions = computed(() => inv.categorias.filter((c) => c.tipo === 'insumo').map((c) => ({ value: c.id, label: c.nombre })))
const emptyQuimico = () => ({ nombre: '', categoria_id: null, unidad: '', cantidad: 0, minimo: '' })
const quimicoForm = ref(emptyQuimico())
const emptyDosis = () => ({ elemento_id: null, cantidad: '', observaciones: '' })
const dosisForm = ref(emptyDosis())

const quimicoCols = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'categoria', label: 'Categoría' },
  { key: 'unidad', label: 'Unidad' },
  { key: 'cantidad', label: 'Disponible', align: 'right', num: true },
  { key: 'minimo', label: 'Mínimo', align: 'right', num: true },
]
const dosisCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'insumo', label: 'Insumo' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'observaciones', label: 'Observaciones' },
]
const quimicoMap = computed(() => Object.fromEntries(inv.quimicos.map((q) => [q.id, q.nombre])))
const quimicoOptionsDisp = computed(() => inv.quimicos.map((q) => ({
  value: q.id, label: `${q.nombre} (${fmtNum(q.cantidad)} ${q.unidad || ''})`.trim(),
})))
const quimicosBajos = computed(() => inv.quimicos.filter((q) => q.minimo != null && Number(q.cantidad) <= Number(q.minimo)).length)
const dosisUnidadInv = computed(() => { const q = inv.quimicos.find((x) => x.id === dosisForm.value.elemento_id); return q?.unidad || '' })

function openNewQuimico() { editingQuimico.value = null; quimicoForm.value = emptyQuimico(); quimicoError.value = ''; showQuimico.value = true }
function openEditQuimico(r) { editingQuimico.value = r; quimicoForm.value = { ...r, categoria_id: r.categoria_id, minimo: r.minimo ?? '' }; quimicoError.value = ''; showQuimico.value = true }
async function saveQuimico() {
  quimicoError.value = ''
  if (!quimicoForm.value.nombre || !quimicoForm.value.categoria_id) { quimicoError.value = 'Nombre y categoría (insumo) son obligatorios.'; return }
  saving.value = true
  try {
    const payload = {
      nombre: quimicoForm.value.nombre,
      categoria_id: Number(quimicoForm.value.categoria_id),
      unidad: quimicoForm.value.unidad || null,
      cantidad: Number(quimicoForm.value.cantidad) || 0,
      minimo: quimicoForm.value.minimo === '' ? null : Number(quimicoForm.value.minimo),
    }
    if (editingQuimico.value) await inv.updateQuimico(editingQuimico.value.id, payload)
    else await inv.createQuimico(payload)
    showQuimico.value = false
    await inv.loadQuimicos()
  } catch (e) { quimicoError.value = apiError(e) } finally { saving.value = false }
}

function openNewDosis() { dosisForm.value = emptyDosis(); dosisError.value = ''; showDosis.value = true }
async function saveDosis() {
  dosisError.value = ''
  if (!dosisForm.value.elemento_id || !dosisForm.value.cantidad || Number(dosisForm.value.cantidad) <= 0) { dosisError.value = 'Seleccione un insumo y una cantidad mayor a 0.'; return }
  saving.value = true
  try {
    await inv.createDosificacionInv({
      elemento_id: Number(dosisForm.value.elemento_id),
      cantidad: Number(dosisForm.value.cantidad),
      observaciones: dosisForm.value.observaciones || null,
    })
    showDosis.value = false
    await inv.loadDosificacionesInv()
    await inv.loadQuimicos()
  } catch (e) { dosisError.value = apiError(e) } finally { saving.value = false }
}

const catMap = computed(() => Object.fromEntries(inv.categorias.map((c) => [c.id, c.nombre])))

const emptyForm = () => ({ nombre: '', categoria_id: null, tipo: '', ubicacion: '', cantidad: 0, unidad: '', proveedor: '', valor: '', minimo: '', observaciones: '' })
const form = ref(emptyForm())
const movForm = ref({ cantidad: '', motivo: '', observaciones: '', fecha: new Date().toISOString().slice(0, 10) })

const elementosCols = [
  { key: 'nombre', label: 'Elemento' },
  { key: 'categoria', label: 'Categoría' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'ubicacion', label: 'Ubicación' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'minimo', label: 'Mín.', align: 'right' },
]
const movCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'elemento', label: 'Elemento' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'motivo', label: 'Motivo' },
]
const alertCols = [
  { key: 'tipo', label: 'Tipo' },
  { key: 'nombre', label: 'Elemento / Producto' },
  { key: 'categoria', label: 'Categoría' },
  { key: 'cantidad', label: 'Cantidad', align: 'right', num: true },
  { key: 'minimo', label: 'Mínimo', align: 'right', num: true },
]

function openNew() { editing.value = null; form.value = emptyForm(); formError.value = ''; showForm.value = true }
function openEdit(row) {
  editing.value = row
  form.value = { ...row, categoria_id: row.categoria_id, valor: row.valor ?? '', minimo: row.minimo ?? '', cantidad: row.cantidad ?? 0 }
  formError.value = ''; showForm.value = true
}
function openMov(row, tipo) { movElem.value = row; movTipo.value = tipo; movForm.value = { cantidad: '', motivo: '', observaciones: '', fecha: new Date().toISOString().slice(0, 10) }; movError.value = ''; showMov.value = true }

async function saveElemento() {
  formError.value = ''
  if (!form.value.nombre || !form.value.categoria_id) { formError.value = 'Nombre y categoría son obligatorios.'; return }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      cantidad: Number(form.value.cantidad) || 0,
      valor: form.value.valor === '' ? null : Number(form.value.valor),
      minimo: form.value.minimo === '' ? null : Number(form.value.minimo),
    }
    if (editing.value) await inv.updateElemento(editing.value.id, payload)
    else await inv.createElemento(payload)
    showForm.value = false
    await inv.loadElementos()
  } catch (e) { formError.value = apiError(e) } finally { saving.value = false }
}

async function saveMov() {
  movError.value = ''
  if (!movForm.value.cantidad || Number(movForm.value.cantidad) <= 0) { movError.value = 'Ingrese una cantidad mayor a 0.'; return }
  saving.value = true
  try {
    await inv.registrarMovimiento(movElem.value.id, movTipo.value, {
      cantidad: Number(movForm.value.cantidad),
      motivo: movForm.value.motivo,
      observaciones: movForm.value.observaciones,
      fecha: movForm.value.fecha,
    })
    showMov.value = false
    await Promise.all([inv.loadElementos(), inv.loadMovimientos(), inv.loadAlertas()])
  } catch (e) { movError.value = apiError(e) } finally { saving.value = false }
}

function badgeTone(tipo) { return tipo === 'entrada' ? 'badge-ok' : 'badge-warn' }

onMounted(async () => {
  await inv.loadCategorias()
  await inv.loadElementos()
  await inv.loadMovimientos()
  await inv.loadAlertas()
  await inv.loadQuimicos()
  await inv.loadDosificacionesInv()
})

watch(() => tab.value, (t) => { if (t === 'quimicos') { inv.loadQuimicos(); inv.loadDosificacionesInv() } })
</script>

<template>
  <div>
    <h1>Inventario</h1>
    <p class="muted">Elementos, movimientos y alertas de existencias (RF-06 a RF-20).</p>

    <div class="tabs">
      <button :class="{ active: tab === 'elementos' }" @click="tab = 'elementos'"><AppIcon name="package" />Elementos</button>
      <button :class="{ active: tab === 'categorias' }" @click="tab = 'categorias'"><AppIcon name="tag" />Categorías</button>
      <button :class="{ active: tab === 'quimicos' }" @click="tab = 'quimicos'"><AppIcon name="flask" />Químicos
        <span v-if="quimicosBajos" class="badge badge-bad">{{ quimicosBajos }}</span>
      </button>
      <button :class="{ active: tab === 'movimientos' }" @click="tab = 'movimientos'"><AppIcon name="refresh" />Movimientos</button>
      <button :class="{ active: tab === 'alertas' }" @click="tab = 'alertas'">
        <AppIcon name="alert" />Alertas
        <span v-if="inv.alertas.length" class="badge badge-bad">{{ inv.alertas.length }}</span>
      </button>
    </div>

    <!-- ELEMENTOS -->
    <div v-if="tab === 'elementos'">
      <div class="filter-bar">
        <div class="field">
          <label>Nombre</label>
          <input class="input" v-model="filtros.nombre" placeholder="Buscar por nombre…" />
        </div>
        <div class="field">
          <label>Categoría</label>
          <select class="select" v-model="filtros.categoria_id">
            <option value="">Todas</option>
            <option v-for="c in catOptions" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
        </div>
        <div class="field filter-actions">
          <button class="btn btn-primary" @click="filtrar"><AppIcon name="search" />Filtrar</button>
          <button class="btn btn-ghost" @click="limpiarFiltros"><AppIcon name="refresh" />Limpiar</button>
        </div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNew"><AppIcon name="plus" />Nuevo elemento</button>
        <button class="btn btn-ghost" @click="refreshInv"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="elementosCols" :rows="inv.elementos" :loading="inv.loading" empty-text="No hay elementos registrados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'categoria'">{{ catMap[row.categoria_id] || '—' }}</span>
          <span v-else-if="col.key === 'minimo'">
            <span class="badge" :class="(row.minimo != null && Number(row.cantidad) <= Number(row.minimo)) ? 'badge-bad' : 'badge-muted'">{{ fmtNum(row.minimo) }}</span>
          </span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEdit(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openMov(row, 'entrada')" title="Entrada"><AppIcon name="plus" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openMov(row, 'salida')" title="Salida"><AppIcon name="download" :size="16" /></button>
          <button v-if="row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="askDelElem(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-else class="btn btn-ghost btn-sm" @click="reactivarElem(row)" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <select class="select" v-model="formatoReporte">
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
          <option value="pdf">PDF</option>
        </select>
        <button class="btn btn-ghost" @click="generarReporte('elementos')"><AppIcon name="download" />Generar reporte</button>
      </div>
      <BaseAlert v-if="repError" type="bad" class="mt-1">{{ repError }}</BaseAlert>
    </div>

    <!-- CATEGORÍAS -->
    <div v-else-if="tab === 'categorias'">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewCat"><AppIcon name="plus" />Nueva categoría</button>
        <button class="btn btn-ghost" @click="refreshInv"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="catCols" :rows="inv.categorias" :loading="inv.loading" empty-text="Sin categorías registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo'" style="text-transform:capitalize">{{ row.tipo }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- QUÍMICOS -->
    <div v-else-if="tab === 'quimicos'">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewQuimico"><AppIcon name="plus" />Nuevo químico</button>
        <button class="btn btn-primary" @click="openNewDosis"><AppIcon name="plus" />Registrar dosificación</button>
        <button class="btn btn-ghost" @click="refreshInv"><AppIcon name="refresh" />Refrescar</button>
      </div>

      <h2 class="section-title">Químicos</h2>
      <DataTable :columns="quimicoCols" :rows="inv.quimicos" :loading="inv.loading" empty-text="Sin químicos registrados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'categoria'">{{ catMap[row.categoria_id] || '—' }}</span>
          <span v-else-if="col.key === 'cantidad'">{{ fmtNum(row.cantidad) }} {{ row.unidad || '' }}</span>
          <span v-else-if="col.key === 'minimo'">
            <span v-if="row.minimo != null && Number(row.cantidad) <= Number(row.minimo)" class="badge badge-bad">Stock bajo</span>
            <span v-else-if="row.minimo != null" class="badge badge-ok">OK</span>
            <span v-else>—</span>
          </span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditQuimico(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <select class="select" v-model="formatoReporte">
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
          <option value="pdf">PDF</option>
        </select>
        <button class="btn btn-ghost" @click="generarReporte('quimicos')"><AppIcon name="download" />Generar reporte</button>
      </div>
      <BaseAlert v-if="repError" type="bad" class="mt-1">{{ repError }}</BaseAlert>

      <h2 class="section-title">Dosificaciones</h2>
      <DataTable :columns="dosisCols" :rows="inv.dosificacionesInv" :loading="inv.loading" empty-text="Sin dosificaciones registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'insumo'">{{ quimicoMap[row.elemento_id] || row.elemento_id }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- MOVIMIENTOS -->
    <div v-else-if="tab === 'movimientos'">
      <DataTable :columns="movCols" :rows="inv.movimientos" :loading="inv.loading" empty-text="Sin movimientos registrados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'elemento'">{{ inv.elementos.find((e) => e.id === row.elemento_id)?.nombre || row.elemento_id }}</span>
          <span v-else-if="col.key === 'tipo'"><span class="badge" :class="badgeTone(row.tipo)">{{ row.tipo }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- ALERTAS -->
    <div v-else>
      <BaseAlert v-if="!inv.alertas.length" type="ok" class="mb-1">No hay elementos ni químicos bajo el mínimo configurado.</BaseAlert>
      <DataTable v-else :columns="alertCols" :rows="inv.alertas" :loading="inv.loading" empty-text="Sin alertas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo'"><span class="badge" :class="row.tipo === 'Químico' ? 'badge-info' : 'badge-muted'">{{ row.tipo }}</span></span>
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
          <label>Tipo</label>
          <input class="input" v-model="form.tipo" placeholder="Ej. accesorio" />
        </div>
        <div class="field">
          <label>Ubicación</label>
          <input class="input" v-model="form.ubicacion" />
        </div>
        <div class="field">
          <label>Cantidad inicial</label>
          <input class="input" type="number" step="0.01" placeholder="0" v-model="form.cantidad" />
        </div>
        <div class="field">
          <label>Unidad</label>
          <input class="input" v-model="form.unidad" placeholder="Ej. unidad, caja" />
        </div>
        <div class="field">
          <label>Mínimo (alerta)</label>
          <input class="input" type="number" step="0.01" placeholder="0" v-model="form.minimo" />
        </div>
        <div class="field">
          <label>Proveedor</label>
          <input class="input" v-model="form.proveedor" />
        </div>
        <div class="field">
          <label>Valor unitario</label>
          <input class="input" type="number" step="0.01" placeholder="0" v-model="form.valor" />
        </div>
      </div>
      <div class="field">
        <label>Observaciones</label>
        <textarea class="textarea" v-model="form.observaciones"></textarea>
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
          <label>Cantidad *</label>
          <input class="input" type="number" step="0.01" placeholder="0" v-model="movForm.cantidad" />
      </div>
      <div class="field">
        <label>Motivo</label>
        <input class="input" v-model="movForm.motivo" :placeholder="movTipo === 'salida' ? 'Ej. instalación, mantenimiento' : 'Ej. compra, donación'" />
      </div>
      <div class="field">
        <label>Fecha</label>
        <input class="input" type="date" v-model="movForm.fecha" />
      </div>
      <div class="field">
        <label>Observaciones</label>
        <textarea class="textarea" v-model="movForm.observaciones"></textarea>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showMov = false">Cancelar</button>
        <button class="btn" :class="movTipo === 'entrada' ? 'btn-primary' : 'btn-danger'" :disabled="saving" @click="saveMov">{{ saving ? 'Guardando…' : 'Registrar' }}</button>
      </template>
    </BaseModal>

    <!-- CATEGORÍA -->
    <BaseModal v-model="showCat" title="Nueva categoría">
      <BaseAlert v-if="catError" type="bad" class="mb-1">{{ catError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="catForm.nombre" /></div>
        <div class="field"><label>Tipo *</label>
          <select class="select" v-model="catForm.tipo">
            <option value="equipo">Equipo</option>
            <option value="herramienta">Herramienta</option>
            <option value="laboratorio">Laboratorio</option>
            <option value="accesorio">Accesorio</option>
            <option value="insumo">Insumo</option>
          </select>
        </div>
        <div class="field" style="grid-column:span 2"><label>Descripción</label><textarea class="textarea" v-model="catForm.descripcion" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showCat = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveCat">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <ConfirmModal v-model:show="confirmShow" title="Inactivar elemento" :message="confirmMsg" confirm-text="Sí, inactivar" danger @confirm="doDelElem" />

    <!-- QUÍMICO (insumo dentro del inventario) -->
    <BaseModal v-model="showQuimico" :title="editingQuimico ? 'Editar químico' : 'Nuevo químico'">
      <BaseAlert v-if="quimicoError" type="bad" class="mb-1">{{ quimicoError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column: span 2"><label>Nombre *</label><input class="input" v-model="quimicoForm.nombre" /></div>
        <div class="field" style="grid-column: span 2"><label>Categoría (insumo) *</label>
          <SearchableSelect v-model="quimicoForm.categoria_id" :options="insumoCatOptions" placeholder="Seleccione la categoría de insumo…" />
        </div>
        <div class="field"><label>Unidad</label><input class="input" v-model="quimicoForm.unidad" placeholder="Ej. kg, L" /></div>
        <div class="field"><label>Cantidad inicial</label><input class="input" type="number" step="0.01" placeholder="0" v-model="quimicoForm.cantidad" /></div>
        <div class="field"><label>Stock mínimo</label><input class="input" type="number" step="0.01" placeholder="0" v-model="quimicoForm.minimo" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showQuimico = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveQuimico">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- DOSIFICACIÓN -->
    <BaseModal v-model="showDosis" title="Registrar dosificación">
      <BaseAlert v-if="dosisError" type="bad" class="mb-1">{{ dosisError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column: span 2"><label>Insumo *</label>
          <SearchableSelect v-model="dosisForm.elemento_id" :options="quimicoOptionsDisp" placeholder="Seleccione un químico/insumo…" />
        </div>
        <div class="field"><label>Cantidad *</label><input class="input" type="number" step="0.01" placeholder="0" v-model="dosisForm.cantidad" /></div>
        <p class="hint" v-if="dosisUnidadInv" style="grid-column: span 2">Unidad del insumo: <strong>{{ dosisUnidadInv }}</strong> (se guarda con la dosificación).</p>
        <div class="field" style="grid-column: span 2"><label>Observaciones</label><textarea class="textarea" v-model="dosisForm.observaciones" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showDosis = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveDosis">{{ saving ? 'Guardando…' : 'Registrar' }}</button>
      </template>
    </BaseModal>
  </div>
</template>
