<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { usePlantaStore } from '../stores/planta'
import { useInventarioStore } from '../stores/inventario'
import { useUsuariosStore } from '../stores/usuarios'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import { apiError, descargarReporte } from '../api/http'
import { fmtNum, fmtRango } from '../utils/format'

const planta = usePlantaStore()
const inv = useInventarioStore()
const usu = useUsuariosStore()
const tab = ref('parametros')
const saving = ref(false)

const paramMap = computed(() => Object.fromEntries(planta.parametros.map((p) => [p.id, p])))
const quimicosBajos = computed(() => inv.quimicos.filter((q) => q.minimo != null && Number(q.cantidad) <= Number(q.minimo)).length)
const userMap = computed(() => Object.fromEntries(usu.usuarios.map((u) => [u.id, u.nombre])))
const userOptions = computed(() => usu.usuarios.map((u) => ({ value: u.id, label: u.nombre })))
const paramOptions = computed(() => planta.parametros.map((p) => ({ value: p.id, label: p.nombre })))

function buildFiltros(obj) {
  const f = {}
  for (const [k, v] of Object.entries(obj)) if (v !== '' && v !== null && v !== undefined) f[k] = v
  return f
}

const formatoReporte = ref('csv')
async function generarReporte(tipo, filtros = {}) {
  const params = { tipo, formato: formatoReporte.value, ...buildFiltros(filtros) }
  try { await descargarReporte('/reportes/planta', params, `reporte_${tipo}`) }
  catch (e) { alert(apiError(e)) }
}

/* Filtros por pestaña */
const medFiltro = ref({ parametro_id: '', fuera_rango: '', fecha_inicio: '', fecha_fin: '' })
function filtrarMed() { planta.loadMediciones(buildFiltros(medFiltro.value)) }
function limpiarMed() { medFiltro.value = { parametro_id: '', fuera_rango: '', fecha_inicio: '', fecha_fin: '' }; planta.loadMediciones() }

const actFiltro = ref({ tipo: '', fecha_inicio: '', fecha_fin: '' })
function filtrarAct() { planta.loadActividades(buildFiltros(actFiltro.value)) }
function limpiarAct() { actFiltro.value = { tipo: '', fecha_inicio: '', fecha_fin: '' }; planta.loadActividades() }

const dosisFiltro = ref({ elemento_id: '', fecha_inicio: '', fecha_fin: '' })
function filtrarDosis() { planta.loadDosificaciones(buildFiltros(dosisFiltro.value)) }
function limpiarDosis() { dosisFiltro.value = { elemento_id: '', fecha_inicio: '', fecha_fin: '' }; planta.loadDosificaciones() }

const horaFiltro = ref({ fecha_inicio: '', fecha_fin: '' })
function filtrarHora() { planta.loadHoras(buildFiltros(horaFiltro.value)) }
function limpiarHora() { horaFiltro.value = { fecha_inicio: '', fecha_fin: '' }; planta.loadHoras() }

function refreshPlanta() {
  return Promise.all([
    planta.loadParametros(), inv.loadCategorias(), inv.loadQuimicos(), planta.loadMediciones(),
    planta.loadFueraRango(), planta.loadActividades(), planta.loadDosificaciones(),
    planta.loadHoras(), usu.loadUsuarios(),
  ])
}

/* Parámetros */
const showParam = ref(false)
const editingParam = ref(null)
const paramError = ref('')
const emptyParam = () => ({ nombre: '', tipo_agua: 'cruda', unidad: '', valor_min: '', valor_max: '' })
const paramForm = ref(emptyParam())
const paramCols = [
  { key: 'nombre', label: 'Parámetro' },
  { key: 'tipo_agua', label: 'Tipo de agua' },
  { key: 'unidad', label: 'Unidad' },
  { key: 'rango', label: 'Rango min / máx' },
]
function openNewParam() { editingParam.value = null; paramForm.value = emptyParam(); paramError.value = ''; showParam.value = true }
function openEditParam(r) { editingParam.value = r; paramForm.value = { ...r, valor_min: r.valor_min ?? '', valor_max: r.valor_max ?? '' }; paramError.value = ''; showParam.value = true }
async function saveParam() {
  paramError.value = ''
  if (!paramForm.value.nombre) { paramError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try {
    const p = { ...paramForm.value, valor_min: paramForm.value.valor_min === '' ? null : Number(paramForm.value.valor_min), valor_max: paramForm.value.valor_max === '' ? null : Number(paramForm.value.valor_max) }
    if (editingParam.value) await planta.updateParametro(editingParam.value.id, p)
    else await planta.createParametro(p)
    showParam.value = false; await planta.loadParametros()
  } catch (e) { paramError.value = apiError(e) } finally { saving.value = false }
}

/* Mediciones */
const showMed = ref(false)
const medError = ref('')
const emptyMed = () => ({ parametro_id: null, valor: '', accion_correctiva: '', observaciones: '' })
const medForm = ref(emptyMed())
const medCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'parametro', label: 'Parámetro' },
  { key: 'tipo_agua', label: 'Tipo de agua' },
  { key: 'valor', label: 'Valor', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'responsable', label: 'Responsable' },
  { key: 'fuera_rango', label: 'Estado' },
  { key: 'accion_correctiva', label: 'Acción correctiva' },
]
/* Pestaña "Fuera de rango": estado ACTUAL por parámetro (última medición) */
const fueraCols = [
  { key: 'parametro', label: 'Parámetro' },
  { key: 'tipo_agua', label: 'Tipo de agua' },
  { key: 'valor', label: 'Último valor', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'rango', label: 'Rango' },
  { key: 'fecha', label: 'Desde' },
  { key: 'hora', label: 'Hora' },
  { key: 'accion_correctiva', label: 'Acción correctiva' },
]
function openNewMed() { medForm.value = emptyMed(); medError.value = ''; showMed.value = true }
async function saveMed() {
  medError.value = ''
  if (!medForm.value.parametro_id || medForm.value.valor === '') { medError.value = 'Parámetro y valor son obligatorios.'; return }
  saving.value = true
  try {
    await planta.createMedicion({
      parametro_id: Number(medForm.value.parametro_id),
      valor: Number(medForm.value.valor),
      accion_correctiva: medForm.value.accion_correctiva || null,
      observaciones: medForm.value.observaciones || null,
    })
    showMed.value = false; await Promise.all([planta.loadMediciones(), planta.loadFueraRango()])
  } catch (e) { medError.value = apiError(e) } finally { saving.value = false }
}

/* Insumos (químicos) + Dosificaciones — los químicos son elementos de inventario */
const insumoCatOptions = computed(() => inv.categorias.filter((c) => c.tipo === 'insumo').map((c) => ({ value: c.id, label: c.nombre })))
const showProd = ref(false)
const editingProd = ref(null)
const showDosis = ref(false)
const prodError = ref('')
const dosisError = ref('')
const emptyProd = () => ({ nombre: '', categoria_id: null, unidad: '', cantidad: 0, minimo: '' })
const prodForm = ref(emptyProd())
const emptyDosis = () => ({ elemento_id: null, cantidad: '', tasa: '', unidad_tasa: 'ml/min', observaciones: '' })
const dosisForm = ref(emptyDosis())
const prodMap = computed(() => Object.fromEntries(inv.quimicos.map((p) => [p.id, p.nombre])))
const prodOptionsDisp = computed(() => inv.quimicos.map((p) => ({
  value: p.id, label: `${p.nombre} (${fmtNum(p.cantidad)} ${p.unidad || ''})`.trim(),
})))
const dosisUnidad = computed(() => {
  const p = inv.quimicos.find((x) => x.id === dosisForm.value.elemento_id)
  return p?.unidad || ''
})
const prodCols = [
  { key: 'nombre', label: 'Insumo' },
  { key: 'unidad', label: 'Unidad' },
  { key: 'cantidad', label: 'Cantidad disponible', align: 'right', num: true },
  { key: 'minimo', label: 'Mínimo', align: 'right', num: true },
  { key: 'estado', label: 'Estado' },
]
const dosisCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'insumo', label: 'Insumo' },
  { key: 'tasa', label: 'Tasa (bomba)' },
  { key: 'cantidad', label: 'Aplicado', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'observaciones', label: 'Observaciones' },
]
function openNewProd() {
  editingProd.value = null
  const qCat = inv.categorias.find((c) => c.tipo === 'insumo' && /quimic/i.test(c.nombre))
  prodForm.value = { ...emptyProd(), categoria_id: qCat ? qCat.id : null }
  prodError.value = ''; showProd.value = true
}
function openEditProd(r) { editingProd.value = r; prodForm.value = { ...r, categoria_id: r.categoria_id, minimo: r.minimo ?? '' }; prodError.value = ''; showProd.value = true }
async function saveProd() {
  prodError.value = ''
  if (!prodForm.value.nombre || !prodForm.value.categoria_id) { prodError.value = 'Nombre y categoría (insumo) son obligatorios.'; return }
  saving.value = true
  try {
    const payload = { nombre: prodForm.value.nombre, categoria_id: Number(prodForm.value.categoria_id), unidad: prodForm.value.unidad || null, cantidad: Number(prodForm.value.cantidad) || 0, minimo: prodForm.value.minimo === '' ? null : Number(prodForm.value.minimo) }
    if (editingProd.value) await inv.updateQuimico(editingProd.value.id, payload)
    else await inv.createQuimico(payload)
    showProd.value = false; await inv.loadQuimicos()
  } catch (e) { prodError.value = apiError(e) } finally { saving.value = false }
}
function openNewDosis() { dosisForm.value = emptyDosis(); dosisError.value = ''; showDosis.value = true }
async function saveDosis() {
  dosisError.value = ''
  if (!dosisForm.value.elemento_id || !dosisForm.value.cantidad) { dosisError.value = 'Insumo y cantidad incorporada son obligatorios.'; return }
  saving.value = true
  try {
    await planta.createDosificacion({
      elemento_id: Number(dosisForm.value.elemento_id),
      // Cantidad INCORPORADA (ej. 1 L): esto descuenta del inventario
      cantidad: Number(dosisForm.value.cantidad),
      // Tasa de la bomba (ej. ml/min): solo informativa, NO descuenta
      tasa: dosisForm.value.tasa === '' ? null : Number(dosisForm.value.tasa),
      unidad_tasa: dosisForm.value.unidad_tasa || 'ml/min',
      observaciones: dosisForm.value.observaciones || null,
    })
     showDosis.value = false; await Promise.all([planta.loadDosificaciones(), inv.loadQuimicos()])
  } catch (e) { dosisError.value = apiError(e) } finally { saving.value = false }
}

/* Resumen "¿para cuánto me queda químico?": por cada químico dosificado,
   stock restante + horas de dosificación continua a la última tasa usada. */
const resumenDosis = computed(() => {
  const map = {}
  for (const d of planta.dosificaciones) { // vienen desc por fecha
    const q = inv.quimicos.find((x) => x.id === d.elemento_id)
    if (!q) continue
    const cur = map[d.elemento_id] || {
      id: d.elemento_id, nombre: q.nombre, unidad: q.unidad || '',
      stock: Number(q.cantidad) || 0, minimo: q.minimo,
      tasa: null, unidadTasa: 'ml/min', ultimaFecha: null,
    }
    if (!cur.ultimaFecha) {
      cur.ultimaFecha = d.fecha
      if (d.tasa != null) { cur.tasa = Number(d.tasa); cur.unidadTasa = d.unidad_tasa || 'ml/min' }
    }
    map[d.elemento_id] = cur
  }
  return Object.values(map).map((r) => {
    const u = r.unidad.toLowerCase()
    let stockMl = null
    if (['l', 'lt', 'litro', 'litros'].includes(u)) stockMl = r.stock * 1000
    else if (['ml', 'mililitro', 'mililitros'].includes(u)) stockMl = r.stock
    r.horasRestantes = (r.tasa && stockMl != null && r.tasa > 0) ? stockMl / (r.tasa * 60) : null
    return r
  })
})

/* ---------------- Horas: gráfico de barras por día ---------------- */
const horasPorDia = computed(() => {
  const map = {}
  for (const h of planta.horas) map[h.fecha] = (map[h.fecha] || 0) + Number(h.horas || 0)
  return Object.entries(map)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([fecha, horas]) => ({ fecha, horas }))
})
const horasTotal = computed(() => horasPorDia.value.reduce((t, d) => t + d.horas, 0))
const horasMax = computed(() => Math.max(...horasPorDia.value.map((d) => d.horas), 0))
function barHeight(h) { return `${(h / (horasMax.value || 1)) * 100}%` }
function diaLabel(f) { const [y, m, d] = String(f).split('-'); return `${d}/${m}` }

/* Actividades */
const showAct = ref(false)
const actError = ref('')
const emptyAct = () => ({ tipo: '', responsable_id: null, observaciones: '', evidencia: '' })
const actForm = ref(emptyAct())
const actCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'responsable', label: 'Responsable' },
  { key: 'estado', label: 'Estado' },
  { key: 'observaciones', label: 'Observaciones' },
  { key: 'evidencia', label: 'Evidencia' },
]
const actTipos = ['Limpieza', 'Desinfección', 'Tanques', 'Bocatoma', 'Mantenimiento']
function openNewAct() { actForm.value = emptyAct(); actError.value = ''; showAct.value = true }
async function saveAct() {
  actError.value = ''
  if (!actForm.value.tipo) { actError.value = 'El tipo de actividad es obligatorio.'; return }
  saving.value = true
  try {
    await planta.createActividad({
      ...actForm.value,
      responsable_id: actForm.value.responsable_id ? Number(actForm.value.responsable_id) : null,
    })
    showAct.value = false; await planta.loadActividades()
  } catch (e) { actError.value = apiError(e) } finally { saving.value = false }
}

/* Horas */
const showHora = ref(false)
const horaError = ref('')
const emptyHora = () => ({ fecha: new Date().toISOString().slice(0, 10), horas: '', responsable_id: null, observaciones: '' })
const horaForm = ref(emptyHora())
const horaCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'horas', label: 'Horas', align: 'right', num: true },
  { key: 'observaciones', label: 'Observaciones' },
]
function openNewHora() { horaForm.value = emptyHora(); horaError.value = ''; showHora.value = true }
async function saveHora() {
  horaError.value = ''
  if (!horaForm.value.horas) { horaError.value = 'Ingrese las horas de servicio.'; return }
  saving.value = true
  try { await planta.createHoraServicio({ fecha: horaForm.value.fecha || new Date().toISOString().slice(0, 10), horas: Number(horaForm.value.horas), responsable_id: horaForm.value.responsable_id ? Number(horaForm.value.responsable_id) : null, observaciones: horaForm.value.observaciones || null }); showHora.value = false; await planta.loadHoras() }
  catch (e) { horaError.value = apiError(e) } finally { saving.value = false }
}

onMounted(async () => {
  await Promise.all([planta.loadParametros(), inv.loadCategorias(), inv.loadQuimicos(), planta.loadMediciones(), planta.loadFueraRango(), planta.loadActividades(), planta.loadDosificaciones(), planta.loadHoras(), usu.loadUsuarios()])
})

/* Al entrar a cada pestaña se refrescan sus datos para no mostrar información desactualizada
   (punto 5: los químicos se actualizan al registrar dosificaciones / al abrir la pestaña). */
watch(tab, (t) => {
  if (t === 'productos') inv.loadQuimicos()
  else if (t === 'dosificaciones') planta.loadDosificaciones()
  else if (t === 'mediciones') planta.loadMediciones()
  else if (t === 'fuera') planta.loadFueraRango()
  else if (t === 'actividades') planta.loadActividades()
  else if (t === 'horas') planta.loadHoras()
})
</script>

<template>
  <div>
    <h1>Planta de tratamiento</h1>
    <p class="muted">Parámetros, mediciones, dosificaciones, actividades y horas de servicio (RF-37 a RF-54).</p>

    <div class="toolbar" style="margin-bottom:1rem">
      <button class="btn btn-ghost" @click="refreshPlanta"><AppIcon name="refresh" />Refrescar</button>
    </div>

    <div class="tabs">
      <button :class="{ active: tab === 'parametros' }" @click="tab = 'parametros'"><AppIcon name="flask" />Parámetros</button>
      <button :class="{ active: tab === 'mediciones' }" @click="tab = 'mediciones'"><AppIcon name="drop" />Mediciones</button>
      <button :class="{ active: tab === 'fuera' }" @click="tab = 'fuera'">
        <AppIcon name="alert" />Fuera de rango
        <span v-if="planta.fueraRango.length" class="badge badge-bad">{{ planta.fueraRango.length }}</span>
      </button>
      <button :class="{ active: tab === 'productos' }" @click="tab = 'productos'"><AppIcon name="flask" />Químicos
        <span v-if="quimicosBajos" class="badge badge-bad">{{ quimicosBajos }}</span>
      </button>
      <button :class="{ active: tab === 'dosificaciones' }" @click="tab = 'dosificaciones'"><AppIcon name="package" />Dosificaciones</button>
      <button :class="{ active: tab === 'actividades' }" @click="tab = 'actividades'"><AppIcon name="wrench" />Actividades</button>
      <button :class="{ active: tab === 'horas' }" @click="tab = 'horas'"><AppIcon name="clock" />Horas de servicio</button>
    </div>

    <!-- PARÁMETROS -->
    <div v-if="tab === 'parametros'">
      <div class="toolbar"><button class="btn btn-primary" @click="openNewParam"><AppIcon name="plus" />Nuevo parámetro</button></div>
      <DataTable :columns="paramCols" :rows="planta.parametros" :loading="planta.loading" empty-text="Sin parámetros configurados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo_agua'" style="text-transform:capitalize">{{ row.tipo_agua }}</span>
          <span v-else-if="col.key === 'rango'">{{ fmtRango(row.valor_min, row.valor_max) }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditParam(row)"><AppIcon name="edit" :size="16" /></button>
        </template>
      </DataTable>
    </div>

    <!-- MEDICIONES -->
    <div v-else-if="tab === 'mediciones'">
      <div class="filter-bar">
        <div class="field"><label>Parámetro</label>
          <select class="select" v-model="medFiltro.parametro_id"><option value="">Todos</option><option v-for="o in paramOptions" :key="o.value" :value="o.value">{{ o.label }}</option></select>
        </div>
        <div class="field"><label>Fuera de rango</label>
          <select class="select" v-model="medFiltro.fuera_rango"><option value="">Todos</option><option value="true">Sí</option><option value="false">No</option></select>
        </div>
        <div class="field"><label>Desde</label><input class="input" type="date" v-model="medFiltro.fecha_inicio" /></div>
        <div class="field"><label>Hasta</label><input class="input" type="date" v-model="medFiltro.fecha_fin" /></div>
        <button class="btn btn-primary" @click="filtrarMed">Filtrar</button>
        <button class="btn btn-ghost" @click="limpiarMed">Limpiar</button>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewMed"><AppIcon name="plus" />Registrar medición</button></div>
      <DataTable :columns="medCols" :rows="planta.mediciones" :loading="planta.loading" empty-text="Sin mediciones registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'parametro'">{{ paramMap[row.parametro_id]?.nombre || row.parametro_id }}</span>
          <span v-else-if="col.key === 'tipo_agua'" style="text-transform:capitalize">{{ paramMap[row.parametro_id]?.tipo_agua || '—' }}</span>
          <span v-else-if="col.key === 'responsable'">{{ userMap[row.responsable_id] || '—' }}</span>
          <span v-else-if="col.key === 'unidad'">{{ paramMap[row.parametro_id]?.unidad || '—' }}</span>
          <span v-else-if="col.key === 'fuera_rango'"><span class="badge" :class="row.fuera_rango ? 'badge-bad' : 'badge-ok'">{{ row.fuera_rango ? 'Fuera de rango' : 'En rango' }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <select class="select" v-model="formatoReporte"><option value="csv">CSV</option><option value="xlsx">XLSX</option><option value="pdf">PDF</option></select>
        <button class="btn btn-ghost" @click="generarReporte('mediciones', medFiltro)">Generar reporte</button>
      </div>
    </div>

    <!-- FUERA DE RANGO (estado actual por parámetro) -->
    <div v-else-if="tab === 'fuera'">
      <p class="muted">Alerta solo si la <strong>última medición</strong> del parámetro está fuera de rango. Las mediciones pasadas se guardan como historial, pero al ajustar y registrar una medición en rango el parámetro deja de alertar.</p>
      <BaseAlert v-if="!planta.fueraRango.length" type="ok" class="mb-1">Todos los parámetros están dentro de su rango según la última medición. ✔</BaseAlert>
      <DataTable v-else :columns="fueraCols" :rows="planta.fueraRango" :loading="planta.loading" empty-text="Sin parámetros fuera de rango.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'parametro'"><strong>{{ row.parametro }}</strong></span>
          <span v-else-if="col.key === 'tipo_agua'" style="text-transform:capitalize">{{ row.tipo_agua }}</span>
          <span v-else-if="col.key === 'rango'"><span class="badge badge-muted">{{ fmtRango(row.valor_min, row.valor_max) }} {{ row.unidad || '' }}</span></span>
          <span v-else-if="col.key === 'valor'"><span class="badge badge-bad">{{ fmtNum(row.valor) }} {{ row.unidad || '' }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </div>

    <!-- INSUMOS / QUÍMICOS (dentro del inventario) -->
    <div v-else-if="tab === 'productos'">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewProd"><AppIcon name="plus" />Nuevo químico</button>
        <button class="btn btn-ghost" @click="refreshPlanta"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="prodCols" :rows="inv.quimicos" :loading="inv.loading" empty-text="Sin químicos/insumos registrados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'cantidad'" class="num">{{ fmtNum(row.cantidad) }} {{ row.unidad || '' }}</span>
          <span v-else-if="col.key === 'minimo'">
            <span v-if="row.minimo != null && Number(row.cantidad) <= Number(row.minimo)" class="badge badge-bad">Stock bajo</span>
            <span v-else-if="row.minimo != null" class="badge badge-ok">OK</span>
            <span v-else>—</span>
          </span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditProd(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <select class="select" v-model="formatoReporte"><option value="csv">CSV</option><option value="xlsx">XLSX</option><option value="pdf">PDF</option></select>
        <button class="btn btn-ghost" @click="generarReporte('quimicos', {})">Generar reporte</button>
      </div>
    </div>

    <!-- DOSIFICACIONES -->
    <div v-else-if="tab === 'dosificaciones'">
      <div class="filter-bar">
        <div class="field"><label>Insumo</label>
          <select class="select" v-model="dosisFiltro.elemento_id"><option value="">Todos</option><option v-for="p in inv.quimicos" :key="p.id" :value="p.id">{{ p.nombre }}</option></select>
        </div>
        <div class="field"><label>Desde</label><input class="input" type="date" v-model="dosisFiltro.fecha_inicio" /></div>
        <div class="field"><label>Hasta</label><input class="input" type="date" v-model="dosisFiltro.fecha_fin" /></div>
        <button class="btn btn-primary" @click="filtrarDosis">Filtrar</button>
        <button class="btn btn-ghost" @click="limpiarDosis">Limpiar</button>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewDosis"><AppIcon name="plus" />Registrar dosificación</button>
        <button class="btn btn-ghost" @click="openNewProd"><AppIcon name="package" />Nuevo químico</button>
      </div>
      <div v-if="resumenDosis.length" class="resumen-ubi">
        <div class="resumen-card" v-for="r in resumenDosis" :key="r.id">
          <span class="resumen-nombre"><AppIcon name="flask" :size="14" />{{ r.nombre }}</span>
          <span class="resumen-dato">Stock: <strong>{{ fmtNum(r.stock) }} {{ r.unidad }}</strong>
            <span v-if="r.minimo != null && r.stock <= Number(r.minimo)" class="badge badge-bad">Crítico</span>
          </span>
          <span class="resumen-dato">Última tasa: <strong>{{ r.tasa != null ? `${fmtNum(r.tasa)} ${r.unidadTasa}` : '—' }}</strong></span>
          <span class="resumen-dato resumen-unidades" v-if="r.horasRestantes != null">≈ {{ fmtNum(r.horasRestantes) }} h de dosificación continua</span>
          <span class="resumen-dato" v-else>Registra la tasa (ml/min) para estimar autonomía</span>
        </div>
      </div>
      <DataTable :columns="dosisCols" :rows="planta.dosificaciones" :loading="planta.loading" empty-text="Sin dosificaciones registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'insumo'">{{ prodMap[row.elemento_id] || row.elemento_id }}</span>
          <span v-else-if="col.key === 'tasa'">{{ row.tasa != null ? `${fmtNum(row.tasa)} ${row.unidad_tasa || 'ml/min'}` : '—' }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <select class="select" v-model="formatoReporte"><option value="csv">CSV</option><option value="xlsx">XLSX</option><option value="pdf">PDF</option></select>
        <button class="btn btn-ghost" @click="generarReporte('dosificaciones', dosisFiltro)">Generar reporte</button>
      </div>
    </div>

    <!-- ACTIVIDADES -->
    <div v-else-if="tab === 'actividades'">
      <div class="filter-bar">
        <div class="field"><label>Tipo</label>
          <select class="select" v-model="actFiltro.tipo"><option value="">Todos</option><option v-for="t in actTipos" :key="t" :value="t">{{ t }}</option></select>
        </div>
        <div class="field"><label>Desde</label><input class="input" type="date" v-model="actFiltro.fecha_inicio" /></div>
        <div class="field"><label>Hasta</label><input class="input" type="date" v-model="actFiltro.fecha_fin" /></div>
        <button class="btn btn-primary" @click="filtrarAct">Filtrar</button>
        <button class="btn btn-ghost" @click="limpiarAct">Limpiar</button>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewAct"><AppIcon name="plus" />Registrar actividad</button></div>
      <DataTable :columns="actCols" :rows="planta.actividades" :loading="planta.loading" empty-text="Sin actividades registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'responsable'">{{ userMap[row.responsable_id] || '—' }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else-if="col.key === 'tipo'" style="text-transform:capitalize">{{ row.tipo }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <select class="select" v-model="formatoReporte"><option value="csv">CSV</option><option value="xlsx">XLSX</option><option value="pdf">PDF</option></select>
        <button class="btn btn-ghost" @click="generarReporte('actividades', actFiltro)">Generar reporte</button>
      </div>
    </div>

    <!-- HORAS -->
    <div v-else>
      <div class="filter-bar">
        <div class="field"><label>Desde</label><input class="input" type="date" v-model="horaFiltro.fecha_inicio" /></div>
        <div class="field"><label>Hasta</label><input class="input" type="date" v-model="horaFiltro.fecha_fin" /></div>
        <button class="btn btn-primary" @click="filtrarHora">Filtrar</button>
        <button class="btn btn-ghost" @click="limpiarHora">Limpiar</button>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewHora"><AppIcon name="plus" />Registrar horas</button></div>

      <div v-if="horasPorDia.length" class="chart-wrap">
        <div class="chart-head">
          <strong>Horas trabajadas por día</strong>
          <span class="muted">Total del periodo: {{ fmtNum(horasTotal) }} h</span>
        </div>
        <div class="chart">
          <div class="chart-col" v-for="d in horasPorDia" :key="d.fecha" :title="`${d.fecha}: ${d.horas} h`">
            <span class="chart-val">{{ fmtNum(d.horas) }}</span>
            <div class="chart-bar" :style="{ height: barHeight(d.horas) }"></div>
            <span class="chart-label">{{ diaLabel(d.fecha) }}</span>
          </div>
        </div>
      </div>

      <DataTable :columns="horaCols" :rows="planta.horas" :loading="planta.loading" empty-text="Sin horas de servicio registradas." />
      <div class="report-bar">
        <label>Formato</label>
        <select class="select" v-model="formatoReporte"><option value="csv">CSV</option><option value="xlsx">XLSX</option><option value="pdf">PDF</option></select>
        <button class="btn btn-ghost" @click="generarReporte('horas', horaFiltro)">Generar reporte</button>
      </div>
    </div>

    <!-- MODALES -->
    <BaseModal v-model="showParam" :title="editingParam ? 'Editar parámetro' : 'Nuevo parámetro'">
      <BaseAlert v-if="paramError" type="bad" class="mb-1">{{ paramError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="paramForm.nombre" placeholder="Ej. pH, cloro residual, turbiedad" /></div>
        <div class="field"><label>Tipo de agua</label>
          <select class="select" v-model="paramForm.tipo_agua"><option value="cruda">Cruda</option><option value="tratada">Tratada</option></select>
        </div>
        <div class="field"><label>Unidad</label><input class="input" v-model="paramForm.unidad" placeholder="Ej. mg/L" /></div>
        <div class="field"><label>Valor mínimo</label><input class="input" type="number" step="0.01" v-model="paramForm.valor_min" placeholder="0" /></div>
        <div class="field"><label>Valor máximo</label><input class="input" type="number" step="0.01" v-model="paramForm.valor_max" placeholder="0" /></div>
      </div>
      <p class="hint">Los rangos mín/máx son configurables; la organización debe confirmarlos según normativa vigente.</p>
      <template #footer>
        <button class="btn btn-ghost" @click="showParam = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveParam">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showMed" title="Registrar medición">
      <BaseAlert v-if="medError" type="bad" class="mb-1">{{ medError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Parámetro *</label>
          <SearchableSelect v-model="medForm.parametro_id" :options="paramOptions" placeholder="Seleccione…" />
        </div>
        <div class="field"><label>Valor *</label><input class="input" type="number" step="0.01" v-model="medForm.valor" placeholder="0" /></div>
      </div>
      <div class="field"><label>Acción correctiva</label><input class="input" v-model="medForm.accion_correctiva" placeholder="Qué se hizo ante un valor fuera de rango" /></div>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="medForm.observaciones"></textarea></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showMed = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveMed">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showProd" :title="editingProd ? 'Editar químico' : 'Nuevo químico'">
      <BaseAlert v-if="prodError" type="bad" class="mb-1">{{ prodError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="prodForm.nombre" /></div>
        <div class="field" style="grid-column:span 2"><label>Categoría (insumo) *</label>
          <SearchableSelect v-model="prodForm.categoria_id" :options="insumoCatOptions" placeholder="Seleccione la categoría de insumo…" />
        </div>
        <div class="field"><label>Unidad</label><input class="input" v-model="prodForm.unidad" placeholder="Ej. kg, L" /></div>
        <div class="field"><label>Cantidad inicial</label><input class="input" type="number" step="0.01" v-model="prodForm.cantidad" placeholder="0" /></div>
        <div class="field"><label>Stock mínimo (alerta)</label><input class="input" type="number" step="0.01" v-model="prodForm.minimo" placeholder="0" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showProd = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveProd">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showDosis" title="Registrar dosificación">
      <BaseAlert v-if="dosisError" type="bad" class="mb-1">{{ dosisError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Insumo *</label>
          <SearchableSelect v-model="dosisForm.elemento_id" :options="prodOptionsDisp" placeholder="Seleccione un químico/insumo…" />
        </div>
        <div class="field"><label>Cantidad incorporada *</label><input class="input" type="number" step="0.01" v-model="dosisForm.cantidad" placeholder="Ej. 1" /></div>
        <div class="field"><label>Tasa de dosificación</label><input class="input" type="number" step="0.1" v-model="dosisForm.tasa" placeholder="Ej. 5" /></div>
        <div class="field"><label>Unidad de tasa</label><input class="input" v-model="dosisForm.unidad_tasa" placeholder="ml/min" /></div>
      </div>
      <p class="hint" v-if="dosisUnidad">Unidad del insumo: <strong>{{ dosisUnidad }}</strong>.</p>
      <p class="hint">La <strong>cantidad incorporada</strong> (ej. 1 L de cloro) <strong>descuenta del inventario</strong>. La <strong>tasa</strong> (ej. ml/min de la bomba) es solo informativa: sirve para estimar cuánto tiempo dura el químico puesto en el tanque.</p>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="dosisForm.observaciones"></textarea></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showDosis = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveDosis">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showAct" title="Registrar actividad de planta">
      <BaseAlert v-if="actError" type="bad" class="mb-1">{{ actError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Tipo de actividad *</label>
          <select class="select" v-model="actForm.tipo">
            <option value="">Seleccione…</option>
            <option v-for="t in actTipos" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>
        <div class="field" style="grid-column:span 2"><label>Responsable</label>
          <SearchableSelect v-model="actForm.responsable_id" :options="userOptions" placeholder="Usuario responsable" clearable />
        </div>
      </div>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="actForm.observaciones"></textarea></div>
      <div class="field"><label>Evidencia (referencia)</label><input class="input" v-model="actForm.evidencia" placeholder="Ej. código de foto, folio" /></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showAct = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveAct">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showHora" title="Registrar horas de servicio">
      <BaseAlert v-if="horaError" type="bad" class="mb-1">{{ horaError }}</BaseAlert>
      <div class="form-row">
        <div class="field"><label>Fecha *</label><input class="input" type="date" v-model="horaForm.fecha" /></div>
        <div class="field"><label>Horas *</label><input class="input" type="number" step="0.5" v-model="horaForm.horas" placeholder="0" /></div>
        <div class="field" style="grid-column:span 2"><label>Responsable</label>
          <SearchableSelect v-model="horaForm.responsable_id" :options="userOptions" placeholder="Usuario responsable" clearable />
        </div>
      </div>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="horaForm.observaciones"></textarea></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showHora = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveHora">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
/* Gráfico de barras de horas de servicio (sin dependencias externas) */
.chart-wrap {
  background: #fff; border: 1px solid var(--acr-borde); border-radius: 10px;
  padding: 1rem; margin-bottom: 1rem;
}
.chart-head { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .75rem; }
.chart {
  display: flex; align-items: stretch; gap: 6px;
  height: 200px; overflow-x: auto; padding-bottom: .25rem;
}
.chart-col {
  flex: 1; min-width: 34px;
  display: flex; flex-direction: column; align-items: center; justify-content: flex-end;
  gap: 2px;
}
.chart-val { font-size: .68rem; color: var(--acr-texto-suave); }
.chart-bar {
  width: 100%; max-width: 42px;
  background: var(--acr-azul); border-radius: 5px 5px 0 0;
  min-height: 2px; transition: height .2s;
}
.chart-label { font-size: .68rem; color: var(--acr-texto-suave); white-space: nowrap; }
</style>
