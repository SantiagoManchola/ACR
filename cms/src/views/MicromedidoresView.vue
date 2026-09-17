<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useMicromedidoresStore } from '../stores/micromedidores'
import { useAuthStore } from '../stores/auth'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import BaseInput from '../components/BaseInput.vue'
import FotoEvidencia from '../components/FotoEvidencia.vue'
import VisorFoto from '../components/VisorFoto.vue'
import { apiError, descargarReporte } from '../api/http'
import { fmtNum, hoyColombia, formatoOptions } from '../utils/format'
import { debounce } from '../utils/debounce'
import { useBusy } from '../utils/async'

const mm = useMicromedidoresStore()
const auth = useAuthStore()
const tab = ref('suscriptores')
/* Cargas de botones asíncronos: deshabilitados hasta resolver la petición */
const { busy: repBusy, run: repRun } = useBusy()
const { busy: refrescando, run: refRun } = useBusy()
const { busy: accionBusy, run: accionRun } = useBusy()
// El fontanero SOLO puede tomar lecturas: sin CRUD de suscriptores ni medidores.
const esFontanero = computed(() => auth.rol === 'fontanero')
const esAdmin = computed(() => auth.rol === 'admin')

const susOptions = computed(() => mm.opcionesSuscriptores.map((s) => ({ value: s.id, label: s.nombre })))
const sectorOptions = computed(() => mm.sectores.map((s) => ({
  value: s.nombre,
  label: s.estado === 'activo' ? s.nombre : `${s.nombre} (inactivo)`,
})))
const sectorActivosOptions = computed(() => mm.sectores
  .filter((s) => s.estado === 'activo')
  .map((s) => ({ value: s.nombre, label: s.nombre })))

const tipoUsuarioOptions = [
  { value: 'residencial', label: 'Residencial' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'oficial', label: 'Oficial' },
  { value: 'otro', label: 'Otro' },
]

const condicionOptions = [
  { value: 'bueno', label: 'Bueno' },
  { value: 'defectuoso', label: 'Defectuoso (se marca)' },
  { value: 'frenado', label: 'Frenado (automático)' },
]
function condicionTone(c) {
  if (c === 'bueno') return 'badge-ok'
  if (c === 'defectuoso') return 'badge-warn'
  return 'badge-bad'
}

/* Confirmación de acciones destructivas */
const confirmShow = ref(false)
const confirmTitle = ref('')
const confirmMsg = ref('')
const pendingDel = ref(null)
function askDel(tipo, r) {
  pendingDel.value = { tipo, id: r.id }
  if (tipo === 'sus') { confirmTitle.value = 'Inactivar suscriptor'; confirmMsg.value = `¿Inactivar al suscriptor «${r.nombre}»?` }
  else if (tipo === 'sec') { confirmTitle.value = 'Inactivar sector'; confirmMsg.value = `¿Inactivar el sector «${r.nombre}»? Ya no será asignable, pero el historial se conserva.` }
  else { confirmTitle.value = 'Inactivar micromedidor'; confirmMsg.value = `¿Inactivar el micromedidor «${r.serial}»?` }
  confirmShow.value = true
}
async function doDel() {
  const p = pendingDel.value
  if (!p) return
  await accionRun(async () => {
    if (p.tipo === 'sus') { await mm.deleteSuscriptor(p.id); await mm.loadSuscriptores(soloNoVacios(filtrosSus.value), pageSus.value, ordenSus.value, dirSus.value) }
    else if (p.tipo === 'sec') { await mm.deleteSector(p.id); await cargarSectores() }
    else { await mm.deleteMicromedidor(p.id); await mm.loadMicromedidores(soloNoVacios(filtrosMm.value), pageMm.value, ordenMm.value, dirMm.value) }
    confirmShow.value = false
    pendingDel.value = null
  })
}
function refrescar() { return refRun(refreshAll) }
function refreshAll() {
  return Promise.all([
    mm.loadSuscriptores(soloNoVacios(filtrosSus.value), pageSus.value),
    mm.loadMicromedidores(soloNoVacios(filtrosMm.value), pageMm.value),
    mm.loadLecturas(soloNoVacios(filtrosLec.value), pageLec.value),
  ])
}

/* ---------------- Filtros (auto-búsqueda con debounce) ---------------- */
const conMedidorOptions = [
  { value: true, label: 'Con medidor' },
  { value: false, label: 'Sin medidor' },
]
const filtrosSus = ref({ nombre: '', identificacion: '', sector: '', tipo_usuario: '', con_medidor: null })
const filtrosMm = ref({ serial: '', suscriptor_id: '', sector: '', condicion: '' })
const filtrosLec = ref({ sector: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
/* Página actual de cada pestaña (paginación server-side) */
const pageSus = ref(1)
const pageMm = ref(1)
const pageLec = ref(1)

function soloNoVacios(obj) {
  const out = {}
  for (const [k, v] of Object.entries(obj)) {
    if (v === '' || v === null || v === undefined) continue
    out[k] = v
  }
  return out
}
/* Orden server-side por pestaña (la API ordena TODA la tabla, no la página) */
const ordenSus = ref(''); const dirSus = ref('asc')
const ordenMm = ref(''); const dirMm = ref('asc')
const ordenLec = ref(''); const dirLec = ref('desc')
function buscarSus() { mm.loadSuscriptores(soloNoVacios(filtrosSus.value), pageSus.value, ordenSus.value, dirSus.value) }
function buscarMm() { mm.loadMicromedidores(soloNoVacios(filtrosMm.value), pageMm.value, ordenMm.value, dirMm.value) }
function buscarLec() { mm.loadLecturas(soloNoVacios(filtrosLec.value), pageLec.value, ordenLec.value, dirLec.value) }

/* Al cambiar cualquier filtro se recarga la página 1 (350 ms tras dejar de escribir) */
const buscarSusDeb = debounce(() => { pageSus.value = 1; buscarSus() })
const buscarMmDeb = debounce(() => { pageMm.value = 1; buscarMm() })
const buscarLecDeb = debounce(() => { pageLec.value = 1; buscarLec() })
watch(filtrosSus, buscarSusDeb, { deep: true })
watch(filtrosMm, buscarMmDeb, { deep: true })
watch(filtrosLec, buscarLecDeb, { deep: true })
function irPaginaSus(p) { pageSus.value = p; buscarSus() }
function irPaginaMm(p) { pageMm.value = p; buscarMm() }
function irPaginaLec(p) { pageLec.value = p; buscarLec() }
/* Cambios de orden: recargar desde la página 1 con el nuevo orden */
function ordenarSus({ key, dir }) { ordenSus.value = key; dirSus.value = dir; pageSus.value = 1; buscarSus() }
function ordenarMm({ key, dir }) { ordenMm.value = key; dirMm.value = dir; pageMm.value = 1; buscarMm() }
function ordenarLec({ key, dir }) { ordenLec.value = key; dirLec.value = dir; pageLec.value = 1; buscarLec() }

/* ---------------- Reportes ---------------- */
const formatoReporte = ref('csv')
const repError = ref('')
async function generarReporte(tipo) {
  repError.value = ''
  const params = { tipo, formato: formatoReporte.value }
  if (tipo === 'suscriptores') Object.assign(params, soloNoVacios(filtrosSus.value))
  else if (tipo === 'micromedidores') Object.assign(params, soloNoVacios(filtrosMm.value))
  else if (tipo === 'lecturas') Object.assign(params, soloNoVacios(filtrosLec.value))
  try {
    await descargarReporte('/reportes/micromedidores', params, `reporte_${tipo}`)
  } catch (e) { repError.value = apiError(e) }
}

/* ---------------- Detalle ---------------- */
const showDetail = ref(false)
const detailSusMmId = ref(null)
/* Tipo de detalle fijado al ABRIR el modal ('sus' | 'mm'): no se infiere de la
   respuesta de la API (el historial de micromedidor incluye el nombre del
   suscriptor, pero eso no lo convierte en detalle de suscriptor) */
const detailTipo = ref('')
// Pestaña dentro del detalle del micromedidor: lecturas | grafico
const detailTab = ref('lecturas')
function openDetailSus(r) {
  detailTipo.value = 'sus'
  detailSusMmId.value = null
  detailTab.value = 'lecturas'
  return mm.loadHistorialSuscriptor(r.id).then(() => {
    const meds = mm.historial?.micromedidores || []
    if (meds.length === 1) detailSusMmId.value = meds[0].id
    showDetail.value = true
  })
}
function openDetailMm(r) {
  detailTipo.value = 'mm'
  detailTab.value = 'lecturas'
  mm.loadHistorialMicromedidor(r.id)
  showDetail.value = true
}

/* ---------------- Suscriptores ---------------- */
const showSus = ref(false)
const editingSus = ref(null)
const susError = ref('')
const saving = ref(false)
const emptySus = () => ({ nombre: '', identificacion: '', codigo_usuario: '', codigo_facturacion: '', tipo_usuario: 'residencial', sector: '', direccion: '' })
const susForm = ref(emptySus())

const susCols = [
  { key: 'nombre', label: 'Nombre', cardTitle: true },
  { key: 'identificacion', label: 'Identificación' },
  { key: 'sector', label: 'Sector' },
  { key: 'tipo_usuario', label: 'Tipo' },
  { key: 'estado', label: 'Estado' },
  { key: 'direccion', label: 'Dirección', wide: true },
]
function openNewSus() { editingSus.value = null; susForm.value = emptySus(); susError.value = ''; showSus.value = true }
function openEditSus(r) { editingSus.value = r; susForm.value = { ...r }; susError.value = ''; showSus.value = true }
async function saveSus() {
  susError.value = ''
  if (!susForm.value.nombre) { susError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try {
    if (editingSus.value) await mm.updateSuscriptor(editingSus.value.id, susForm.value)
    else await mm.createSuscriptor(susForm.value)
    showSus.value = false
    await mm.loadSuscriptores(soloNoVacios(filtrosSus.value), pageSus.value)
    await mm.loadSuscriptoresOpciones()
  } catch (e) { susError.value = apiError(e) } finally { saving.value = false }
}
async function delSus(r) { askDel('sus', r) }
async function reactivarSus(r) {
  await accionRun(async () => {
    await mm.updateSuscriptor(r.id, { estado: 'activo' })
    await mm.loadSuscriptores(soloNoVacios(filtrosSus.value), pageSus.value, ordenSus.value, dirSus.value)
    await mm.loadSuscriptoresOpciones()
  })
}

/* ---------------- Sectores (catálogo, solo admin) ---------------- */
const showSec = ref(false)
const editingSec = ref(null)
const secError = ref('')
const secForm = ref({ nombre: '' })
const conteoSec = ref({})
const secCols = [
  { key: 'nombre', label: 'Sector', cardTitle: true },
  { key: 'suscriptores', label: 'Suscriptores', align: 'right', num: true },
  { key: 'estado', label: 'Estado' },
]
async function cargarSectores() {
  await mm.loadSectores()
  if (esAdmin.value) {
    try { conteoSec.value = await mm.loadConteoSectores() } catch { conteoSec.value = {} }
  }
}
function openNewSec() { editingSec.value = null; secForm.value = { nombre: '' }; secError.value = ''; showSec.value = true }
function openEditSec(r) { editingSec.value = r; secForm.value = { nombre: r.nombre }; secError.value = ''; showSec.value = true }
async function saveSec() {
  secError.value = ''
  if (!secForm.value.nombre || !secForm.value.nombre.trim()) { secError.value = 'El nombre es obligatorio.'; return }
  saving.value = true
  try {
    if (editingSec.value) await mm.updateSector(editingSec.value.id, { nombre: secForm.value.nombre.trim() })
    else await mm.createSector({ nombre: secForm.value.nombre.trim() })
    showSec.value = false; await cargarSectores()
  } catch (e) { secError.value = apiError(e) } finally { saving.value = false }
}
async function delSec(r) { askDel('sec', r) }
async function reactivarSec(r) {
  await accionRun(async () => {
    await mm.updateSector(r.id, { estado: 'activo' })
    await cargarSectores()
  })
}

/* ---------------- Micromedidores ---------------- */
const showMm = ref(false)
const editingMm = ref(null)
const mmError = ref('')
const emptyMm = () => ({ serial: '', tipo: '', suscriptor_id: null, direccion: '', fecha_instalacion: '', condicion: 'bueno' })
const mmForm = ref(emptyMm())

const mmCols = [
  { key: 'serial', label: 'Serial', cardTitle: true },
  { key: 'tipo', label: 'Tipo' },
  { key: 'suscriptor', label: 'Suscriptor', sortValue: (r) => r.suscriptor_nombre || '' },
  { key: 'direccion', label: 'Dirección', wide: true },
  { key: 'fecha_instalacion', label: 'Instalación' },
  { key: 'condicion', label: 'Condición' },
  { key: 'estado', label: 'Estado' },
]
function openNewMm() { editingMm.value = null; mmForm.value = emptyMm(); mmError.value = ''; showMm.value = true }
function openEditMm(r) { editingMm.value = r; mmForm.value = { ...r, condicion: r.condicion || 'bueno' }; mmError.value = ''; showMm.value = true }
async function saveMm() {
  mmError.value = ''
  if (!mmForm.value.serial) { mmError.value = 'El serial es obligatorio.'; return }
  saving.value = true
  try {
    const payload = { ...mmForm.value }
    if (editingMm.value) delete payload.suscriptor_id // un medidor no cambia de suscriptor
    if (editingMm.value) await mm.updateMicromedidor(editingMm.value.id, payload)
    else await mm.createMicromedidor(payload)
    showMm.value = false; await mm.loadMicromedidores(soloNoVacios(filtrosMm.value), pageMm.value)
  } catch (e) { mmError.value = apiError(e) } finally { saving.value = false }
}
async function delMm(r) { askDel('mm', r) }
async function reactivarMm(r) {
  await accionRun(async () => {
    await mm.updateMicromedidor(r.id, { estado: 'activo' })
    await mm.loadMicromedidores(soloNoVacios(filtrosMm.value), pageMm.value, ordenMm.value, dirMm.value)
  })
}

/* Visor de evidencias fotográficas (miniaturas en tablas -> foto grande) */
const visorShow = ref(false)
const visorSrc = ref('')
const visorTitulo = ref('Evidencia')
function verFoto(url, titulo = 'Evidencia') {
  if (!url) return
  visorSrc.value = url
  visorTitulo.value = titulo
  visorShow.value = true
}

/* ---------------- Lecturas ---------------- */
const showLec = ref(false)
const lecError = ref('')
const emptyLec = () => ({ micromedidor_id: null, suscriptor_id: null, lectura: '', estimada: false, novedad: '', irregular: false, foto_url: '' })
const lecForm = ref(emptyLec())
const fotoLecRef = ref(null)

const lecCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'suscriptor', label: 'Suscriptor', cardTitle: true, sortValue: (r) => r.suscriptor_nombre || '' },
  { key: 'micromedidor_id', label: 'Medidor', sortValue: (r) => r.medidor_serial || '' },
  { key: 'lectura', label: 'Lectura', align: 'right' },
  { key: 'consumo', label: 'Consumo', align: 'right' },
  { key: 'tipo', label: 'Tipo', sortValue: (r) => (r.promedio_usado ? 'estimada' : 'física') },
  { key: 'foto', label: 'Foto', sortable: false },
  { key: 'novedad', label: 'Novedad', wide: true },
]
const detailLecCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'lectura', label: 'Lectura', align: 'right', num: true },
  { key: 'consumo', label: 'Consumo', align: 'right', num: true },
  { key: 'tipo', label: 'Tipo', sortValue: (r) => (r.promedio_usado ? 'estimada' : 'física') },
  { key: 'foto', label: 'Foto', sortable: false },
  { key: 'novedad', label: 'Novedad', wide: true },
]
const detailIsSus = computed(() => detailTipo.value === 'sus')
const detailEntity = computed(() => (detailIsSus.value ? mm.historial?.suscriptor : mm.historial?.micromedidor) || null)
/* En el detalle del suscriptor las lecturas se discriminan por medidor */
const susMmOptions = computed(() => (mm.historial?.micromedidores || []).map((m) => ({
  value: m.id,
  label: `${m.serial}${m.estado === 'inactivo' ? ' (inactivo)' : ''}`,
})))
const detailLecturas = computed(() => {
  const lecturas = mm.historial?.lecturas || []
  if (detailIsSus.value) return lecturas.filter((l) => l.micromedidor_id === detailSusMmId.value)
  return lecturas
})

/* -------- Promedio histórico de consumo (validado, misma regla del backend) ----
   Regla: promedio de los consumos de las ÚLTIMAS 6 lecturas con consumo no nulo.
   Se prefiere el valor calculado por el backend (historial.promedio_historico);
   si no viene (historial de suscriptor o backend anterior) se calcula en cliente. */
function calcularPromedioLocal(lecturas) {
  const consumos = (lecturas || [])
    .slice()
    .sort((a, b) => {
      const f = String(a.fecha).localeCompare(String(b.fecha))
      if (f !== 0) return f
      const h = String(a.hora || '').localeCompare(String(b.hora || ''))
      if (h !== 0) return h
      return Number(a.id || 0) - Number(b.id || 0)
    })
    .map((l) => (l.consumo === null || l.consumo === undefined || l.consumo === '' ? null : Number(l.consumo)))
    .filter((c) => c !== null && !Number.isNaN(c))
    .slice(-6)
  if (!consumos.length) return { promedio: null, base: 0 }
  const suma = consumos.reduce((t, c) => t + c, 0)
  return { promedio: suma / consumos.length, base: consumos.length }
}
const promedioLocal = computed(() => calcularPromedioLocal(detailIsSus.value ? detailLecturas.value : (mm.historial?.lecturas || [])))
const promedioHistorico = computed(() => {
  const back = mm.historial?.promedio_historico
  if (back !== null && back !== undefined && back !== '' && !Number.isNaN(Number(back))) return Number(back)
  return promedioLocal.value.promedio
})
const promedioBaseN = computed(() => {
  const back = mm.historial?.promedio_base_n
  if (back !== null && back !== undefined && back !== '') return Number(back)
  return promedioLocal.value.base
})
const promedioTexto = computed(() => (
  promedioHistorico.value === null || promedioHistorico.value === undefined
    ? '— (sin consumos históricos)'
    : `${fmtNum(promedioHistorico.value)} m³ (últimas ${promedioBaseN.value} lectura(s))`
))

/* -------- Gráfico: últimas 6 mediciones (consumo en m³) -------- */
const ultimas6 = computed(() => {
  const lecturas = detailIsSus.value ? detailLecturas.value : (mm.historial?.lecturas || [])
  return lecturas
    .slice()
    .sort((a, b) => {
      const f = String(a.fecha).localeCompare(String(b.fecha))
      if (f !== 0) return f
      const h = String(a.hora || '').localeCompare(String(b.hora || ''))
      if (h !== 0) return h
      return Number(a.id || 0) - Number(b.id || 0)
    })
    .slice(-6)
    .map((l) => ({
      ...l,
      consumoNum: l.consumo === null || l.consumo === undefined || l.consumo === '' ? null : Number(l.consumo),
      mesCorto: (MESES.find((m) => m.v === Number(String(l.fecha).slice(5, 7)))?.label || '—').slice(0, 3),
    }))
})
const maxConsumoChart = computed(() => {
  const vals = ultimas6.value.map((l) => l.consumoNum).filter((c) => c !== null && !Number.isNaN(c))
  return vals.length ? Math.max(...vals, 0) : 0
})
function alturaBarra(consumo) {
  if (consumo === null || consumo === undefined || Number.isNaN(consumo)) return 2
  if (!maxConsumoChart.value) return 2
  const pct = (Number(consumo) / maxConsumoChart.value) * 100
  return Math.max(4, Math.min(100, pct))
}
const totalUltimas6 = computed(() => ultimas6.value.reduce((t, l) => t + (l.consumoNum || 0), 0))
const chartPeriodo = computed(() => {
  if (!ultimas6.value.length) return '—'
  const ini = ultimas6.value[0].fecha
  const fin = ultimas6.value[ultimas6.value.length - 1].fecha
  return ini === fin ? String(ini) : `${ini} – ${fin}`
})

/* ---------------- Impresión de mediciones ---------------- */
const MESES = [
  { v: 1, label: 'Enero' }, { v: 2, label: 'Febrero' }, { v: 3, label: 'Marzo' },
  { v: 4, label: 'Abril' }, { v: 5, label: 'Mayo' }, { v: 6, label: 'Junio' },
  { v: 7, label: 'Julio' }, { v: 8, label: 'Agosto' }, { v: 9, label: 'Septiembre' },
  { v: 10, label: 'Octubre' }, { v: 11, label: 'Noviembre' }, { v: 12, label: 'Diciembre' },
]
const showPrint = ref(false)
const printForm = ref({ anio: '', mes_inicio: '', mes_fin: '' })
const aniosDisponibles = computed(() => {
  const anios = new Set((mm.historial?.lecturas || []).map((l) => Number(String(l.fecha).slice(0, 4))))
  return [...anios].sort((a, b) => b - a)
})
const aniosOptions = computed(() => aniosDisponibles.value.map((a) => ({ value: a, label: String(a) })))
const mesesOptions = computed(() => MESES.map((m) => ({ value: m.v, label: m.label })))
const printRows = computed(() => {
  const { anio, mes_inicio, mes_fin } = printForm.value
  return (mm.historial?.lecturas || [])
    .filter((l) => {
      if (!anio) return false
      const f = String(l.fecha)
      if (Number(f.slice(0, 4)) !== Number(anio)) return false
      const mes = Number(f.slice(5, 7))
      if (mes_inicio && mes < Number(mes_inicio)) return false
      if (mes_fin && mes > Number(mes_fin)) return false
      return true
    })
    .slice()
    .sort((a, b) => String(a.fecha).localeCompare(String(b.fecha)))
    .map((l) => ({
      ...l,
      mes: MESES.find((m) => m.v === Number(String(l.fecha).slice(5, 7)))?.label || '—',
    }))
})
const printTotal = computed(() => printRows.value.reduce((t, l) => t + Number(l.consumo || 0), 0))
const printPeriodo = computed(() => {
  const { anio, mes_inicio, mes_fin } = printForm.value
  if (!anio) return '—'
  const ini = MESES.find((m) => m.v === Number(mes_inicio))?.label
  const fin = MESES.find((m) => m.v === Number(mes_fin))?.label
  if (ini && fin) return `${ini} – ${fin} de ${anio}`
  if (ini) return `${ini} – Diciembre de ${anio}`
  if (fin) return `Enero – ${fin} de ${anio}`
  return `Año ${anio}`
})
function abrirPrint() {
  const hoy = new Date()
  printForm.value = {
    anio: aniosDisponibles.value[0] || hoy.getFullYear(),
    mes_inicio: '',
    mes_fin: '',
  }
  showPrint.value = true
}
/* Impresión del gráfico de últimas 6 mediciones: mismo mecanismo (window.print),
   con su propia área de impresión. Solo un modal de impresión vive a la vez,
   así que el CSS @media print existente la captura sin cambios. */
const showPrintChart = ref(false)
function abrirPrintChart() { showPrintChart.value = true }
function imprimir() { window.print() }
function onPickMedidor(val) {
  const id = val ?? lecForm.value.micromedidor_id
  const m = (mm.opcionesMedidores || []).find((x) => x.id === id)
  if (m && m.suscriptor_id) lecForm.value.suscriptor_id = m.suscriptor_id
}
/* Medidores disponibles para registrar lectura: solo ACTIVOS; si hay suscriptor
   seleccionado, únicamente los medidores de ese suscriptor. */
const lecMmOptions = computed(() => {
  const activos = (mm.opcionesMedidores || []).filter((m) => m.estado === 'activo')
  const lista = lecForm.value.suscriptor_id
    ? activos.filter((m) => m.suscriptor_id === lecForm.value.suscriptor_id)
    : activos
  return lista.map((m) => ({ value: m.id, label: m.serial }))
})
watch(() => lecForm.value.suscriptor_id, (sid) => {
  const activos = (mm.opcionesMedidores || []).filter((m) => m.estado === 'activo' && m.suscriptor_id === sid)
  if (activos.length === 1) {
    // Un solo medidor asociado: se selecciona automáticamente
    lecForm.value.micromedidor_id = activos[0].id
  } else if (!sid || !activos.some((m) => m.id === lecForm.value.micromedidor_id)) {
    lecForm.value.micromedidor_id = null
  }
})
function openNewLec() { lecForm.value = emptyLec(); lecError.value = ''; showLec.value = true }
async function saveLec() {
  lecError.value = ''
  if (!lecForm.value.micromedidor_id || !lecForm.value.suscriptor_id) { lecError.value = 'Medidor y suscriptor son obligatorios.'; return }
  if (!lecForm.value.estimada && lecForm.value.lectura === '') { lecError.value = 'Ingrese el valor del medidor o marque la lectura como estimada.'; return }
  if (fotoLecRef.value?.ocupado()) { lecError.value = 'Espera a que termine de subir la foto.'; return }
  saving.value = true
  try {
    const payload = {
      micromedidor_id: Number(lecForm.value.micromedidor_id),
      suscriptor_id: Number(lecForm.value.suscriptor_id),
      novedad: lecForm.value.novedad || null,
      // Estimada: sin valor de medidor; el backend lo calcula (previa + promedio)
      irregular: !!lecForm.value.estimada,
      foto_url: lecForm.value.foto_url || null,
    }
    if (!lecForm.value.estimada) payload.lectura = Number(lecForm.value.lectura)
    await mm.createLectura(payload)
    showLec.value = false
    await mm.loadLecturas()
    // La condición (frenado automático) puede cambiar con esta lectura
    await mm.loadMicromedidores()
    if (showDetail.value && detailEntity.value) {
      if (detailIsSus.value) await mm.loadHistorialSuscriptor(detailEntity.value.id)
      else await mm.loadHistorialMicromedidor(detailEntity.value.id)
    }
  } catch (e) { lecError.value = apiError(e) } finally { saving.value = false }
}

onMounted(async () => {
  await mm.loadSuscriptoresOpciones()
  await mm.loadMicromedidoresOpciones()
  buscarSus()
  buscarMm()
  buscarLec()
  await mm.loadSectores()
})
</script>

<template>
  <div class="view-fit">
    <h1>Micromedidores</h1>
    <p class="muted">Suscriptores, medidores y lecturas.</p>
    <BaseAlert v-if="repError" type="bad" class="mb-1">{{ repError }}</BaseAlert>

    <div class="tabs">
      <button :class="{ active: tab === 'suscriptores' }" @click="tab = 'suscriptores'"><AppIcon name="users" />Suscriptores</button>
      <button :class="{ active: tab === 'micromedidores' }" @click="tab = 'micromedidores'"><AppIcon name="gauge" />Micromedidores</button>
      <button :class="{ active: tab === 'lecturas' }" @click="tab = 'lecturas'"><AppIcon name="edit" />Lecturas</button>
      <button v-if="esAdmin" :class="{ active: tab === 'sectores' }" @click="tab = 'sectores'"><AppIcon name="mapPin" />Sectores</button>
    </div>

    <!-- SUSCRIPTORES -->
    <div v-if="tab === 'suscriptores'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Nombre</label><BaseInput v-model="filtrosSus.nombre" placeholder="Escriba para buscar…" /></div>
        <div class="field"><label>Identificación</label><BaseInput v-model="filtrosSus.identificacion" placeholder="Escriba para buscar…" /></div>
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosSus.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Tipo de usuario</label>
          <SearchableSelect v-model="filtrosSus.tipo_usuario" :options="tipoUsuarioOptions" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Medidor</label>
          <SearchableSelect v-model="filtrosSus.con_medidor" :options="conMedidorOptions" placeholder="Todos" clearable />
        </div>
      </div>
      <div class="toolbar">
        <button v-if="!esFontanero" class="btn btn-primary" @click="openNewSus"><AppIcon name="plus" />Nuevo suscriptor</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refrescar"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable
        :columns="susCols" :rows="mm.suscriptores" :loading="mm.loading"
        :total="mm.suscriptoresTotal" :page="pageSus" :page-size="20"
        :sort-by="ordenSus" :sort-dir="dirSus"
        empty-text="Sin suscriptores."
        @update:page="irPaginaSus"
        @update:sort="ordenarSus"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo_usuario'" style="text-transform:capitalize">{{ row.tipo_usuario }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button v-if="!esFontanero" class="btn btn-ghost btn-sm" @click="openEditSus(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openDetailSus(row)" title="Detalle"><AppIcon name="eye" :size="16" /></button>
          <button v-if="!esFontanero && row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="delSus(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-if="!esFontanero && row.estado !== 'activo'" class="btn btn-ghost btn-sm" :disabled="accionBusy" @click="accionRun(() => reactivarSus(row))" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
      <div v-if="!esFontanero" class="report-bar">
        <span class="muted">Reporte de suscriptores:</span>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('suscriptores'))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- MICROMEDIDORES -->
    <div v-else-if="tab === 'micromedidores'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Serial</label><BaseInput v-model="filtrosMm.serial" placeholder="Escriba para buscar…" /></div>
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosMm.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Suscriptor</label>
          <SearchableSelect v-model="filtrosMm.suscriptor_id" :options="susOptions" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Condición</label>
          <SearchableSelect v-model="filtrosMm.condicion" :options="condicionOptions" placeholder="Todas" clearable />
        </div>
      </div>
      <div class="toolbar">
        <button v-if="!esFontanero" class="btn btn-primary" @click="openNewMm"><AppIcon name="plus" />Nuevo micromedidor</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refrescar"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable
        :columns="mmCols" :rows="mm.micromedidores" :loading="mm.loading"
        :total="mm.micromedidoresTotal" :page="pageMm" :page-size="20"
        :sort-by="ordenMm" :sort-dir="dirMm"
        empty-text="Sin micromedidores."
        @update:page="irPaginaMm"
        @update:sort="ordenarMm"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'suscriptor'">{{ row.suscriptor_nombre || '—' }}</span>
          <span v-else-if="col.key === 'condicion'"><span class="badge" :class="condicionTone(row.condicion)" style="text-transform:capitalize">{{ row.condicion || 'bueno' }}</span></span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button v-if="!esFontanero" class="btn btn-ghost btn-sm" @click="openEditMm(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openDetailMm(row)" title="Detalle"><AppIcon name="eye" :size="16" /></button>
          <button v-if="!esFontanero && row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="delMm(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-if="!esFontanero && row.estado !== 'activo'" class="btn btn-ghost btn-sm" :disabled="accionBusy" @click="accionRun(() => reactivarMm(row))" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
      <div v-if="!esFontanero" class="report-bar">
        <span class="muted">Reporte de micromedidores:</span>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('micromedidores'))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- LECTURAS -->
    <div v-else-if="tab === 'lecturas'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosLec.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Fecha inicio</label><BaseInput v-model="filtrosLec.fecha_inicio" type="date" /></div>
        <div class="field"><label>Fecha fin</label><BaseInput v-model="filtrosLec.fecha_fin" type="date" /></div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewLec"><AppIcon name="plus" />Registrar lectura</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refrescar"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable
        :columns="lecCols" :rows="mm.lecturas" :loading="mm.loading"
        :total="mm.lecturasTotal" :page="pageLec" :page-size="20"
        :sort-by="ordenLec" :sort-dir="dirLec"
        empty-text="Sin lecturas registradas."
        @update:page="irPaginaLec"
        @update:sort="ordenarLec"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'suscriptor'">{{ row.suscriptor_nombre || row.suscriptor_id }}</span>
          <span v-else-if="col.key === 'micromedidor_id'">{{ row.medidor_serial || row.micromedidor_id }}</span>
          <span v-else-if="col.key === 'tipo'"><span class="badge" :class="row.promedio_usado ? 'badge-info' : 'badge-muted'" :title="row.promedio_usado ? 'Consumo estimado con el promedio histórico (no fue posible tomar la medición)' : 'Medición física del medidor'">{{ row.promedio_usado ? 'Estimada' : 'Física' }}</span></span>
          <span v-else-if="col.key === 'foto'">
            <img v-if="row.foto_url" :src="row.foto_url" class="mini-foto" alt="Evidencia" loading="lazy"
              @click="verFoto(row.foto_url, `${row.medidor_serial || 'Medidor'} · ${row.fecha}`)" />
            <span v-else class="muted">—</span>
          </span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div v-if="!esFontanero" class="report-bar">
        <span class="muted">Reporte de lecturas:</span>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('lecturas'))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- SECTORES (catálogo, solo admin) -->
    <div v-else-if="tab === 'sectores'" class="tab-panel">
      <p class="muted">Catálogo de sectores para clasificar suscriptores. Solo el admin puede agregar, renombrar o inactivar. Un sector inactivo ya no es asignable, pero el historial se conserva.</p>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewSec"><AppIcon name="plus" />Nuevo sector</button>
        <button class="btn btn-ghost" @click="cargarSectores"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="secCols" :rows="mm.sectores" :loading="mm.loading" empty-text="Sin sectores en el catálogo.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'suscriptores'" :style="{ textAlign: col.align }">{{ conteoSec[row.nombre] ?? '—' }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditSec(row)" title="Renombrar"><AppIcon name="edit" :size="16" /></button>
          <button v-if="row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="delSec(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-else class="btn btn-ghost btn-sm" :disabled="accionBusy" @click="accionRun(() => reactivarSec(row))" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
    </div>

    <!-- MODAL SUSCRIPTOR -->
    <BaseModal v-model="showSus" :title="editingSus ? 'Editar suscriptor' : 'Nuevo suscriptor'">
      <BaseAlert v-if="susError" type="bad" class="mb-1">{{ susError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="susForm.nombre" /></div>
        <div class="field"><label>Identificación</label><input class="input" v-model="susForm.identificacion" /></div>
        <div class="field"><label>Tipo de usuario</label>
          <SearchableSelect v-model="susForm.tipo_usuario" :options="tipoUsuarioOptions" placeholder="Tipo de usuario" />
        </div>
        <div class="field"><label>Sector / barrio</label>
          <SearchableSelect v-model="susForm.sector" :options="sectorActivosOptions" placeholder="Seleccione un sector del catálogo" clearable />
          <p class="hint">Solo sectores activos del catálogo (pestaña Sectores, solo admin).</p>
        </div>
        <div class="field"><label>Código de usuario</label><input class="input" v-model="susForm.codigo_usuario" /></div>
        <div class="field"><label>Código de facturación</label><input class="input" v-model="susForm.codigo_facturacion" /></div>
        <div class="field" style="grid-column:span 2"><label>Dirección</label><input class="input" v-model="susForm.direccion" /></div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showSus = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveSus">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- MODAL SECTOR -->
    <BaseModal v-model="showSec" :title="editingSec ? 'Renombrar sector' : 'Nuevo sector'">
      <BaseAlert v-if="secError" type="bad" class="mb-1">{{ secError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="secForm.nombre" placeholder="Ej. VILLA NUEVA" style="text-transform:uppercase" /></div>
      </div>
      <p v-if="editingSec" class="hint">Al renombrar, los suscriptores de «{{ editingSec.nombre }}» se actualizan automáticamente.</p>
      <p v-else class="hint">Se recomienda en mayúsculas. Quedará disponible de inmediato en filtros y formularios.</p>
      <template #footer>
        <button class="btn btn-ghost" @click="showSec = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveSec">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- MODAL MICROMEDIDOR -->
    <BaseModal v-model="showMm" :title="editingMm ? 'Editar micromedidor' : 'Nuevo micromedidor'">
      <BaseAlert v-if="mmError" type="bad" class="mb-1">{{ mmError }}</BaseAlert>
      <div class="form-row">
        <div class="field"><label>Serial *</label><input class="input" v-model="mmForm.serial" /></div>
        <div class="field"><label>Tipo</label><input class="input" v-model="mmForm.tipo" placeholder="Ej. analógico, digital" /></div>
        <div class="field" style="grid-column:span 2"><label>Suscriptor</label>
          <SearchableSelect v-model="mmForm.suscriptor_id" :options="susOptions" placeholder="Sin asignar" clearable :disabled="!!editingMm" />
          <p v-if="editingMm" class="hint">Un medidor no cambia de suscriptor: la asignación se define al crearlo.</p>
        </div>
        <div class="field" style="grid-column:span 2"><label>Dirección</label><input class="input" v-model="mmForm.direccion" /></div>
        <div class="field"><label>Fecha de instalación</label><BaseInput v-model="mmForm.fecha_instalacion" type="date" /></div>
        <div class="field"><label>Condición</label>
          <SearchableSelect v-model="mmForm.condicion" :options="condicionOptions" placeholder="Condición" />
          <p class="hint">«Frenado» se detecta solo con 3 lecturas mensuales idénticas seguidas.</p>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showMm = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveMm">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <!-- MODAL LECTURA -->
    <BaseModal v-model="showLec" title="Registrar lectura">
      <BaseAlert v-if="lecError" type="bad" class="mb-1">{{ lecError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Suscriptor *</label>
          <SearchableSelect v-model="lecForm.suscriptor_id" :options="susOptions" placeholder="Seleccione…" />
        </div>
        <div class="field" style="grid-column:span 2"><label>Micromedidor (activos) *</label>
          <SearchableSelect v-model="lecForm.micromedidor_id" :options="lecMmOptions" placeholder="Se filtran por el suscriptor" @update:model-value="onPickMedidor" />
          <p class="hint">Si el suscriptor tiene un solo medidor activo se selecciona automáticamente; solo se listan medidores activos.</p>
        </div>
        <div class="field" v-if="!lecForm.estimada"><label>Lectura (m³) *</label><input class="input" type="number" step="1" placeholder="0" v-model="lecForm.lectura" /></div>
        <div class="field" v-else>
          <label>Valor del medidor</label>
          <input class="input" disabled placeholder="Se calculará automáticamente (lectura previa + promedio histórico)" />
        </div>
      </div>
      <div class="field">
        <label class="flex center gap-1" style="font-weight:600;cursor:pointer">
          <input type="checkbox" v-model="lecForm.estimada" /> Lectura estimada — no fue posible tomar la medición (el sistema calcula el valor del medidor con la lectura previa + promedio histórico)
        </label>
        <p class="hint">Según el procedimiento de Acuaricaurte, ante la falta de lectura se usa el promedio histórico.</p>
      </div>
      <div class="field">
        <label>Novedad</label>
        <textarea class="textarea" v-model="lecForm.novedad" placeholder="Observación o novedad de la lectura"></textarea>
      </div>
      <FotoEvidencia ref="fotoLecRef" v-model="lecForm.foto_url" modulo="lectura" />
      <template #footer>
        <button class="btn btn-ghost" @click="showLec = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveLec">{{ saving ? 'Guardando…' : 'Guardar lectura' }}</button>
      </template>
    </BaseModal>

    <!-- MODAL DETALLE -->
    <BaseModal v-model="showDetail" :title="detailIsSus ? 'Detalle de suscriptor' : 'Detalle de micromedidor'">
      <div v-if="detailEntity" class="detail-grid">
        <template v-if="detailIsSus">
          <div><strong>Nombre:</strong> {{ detailEntity.nombre }}</div>
          <div><strong>Identificación:</strong> {{ detailEntity.identificacion }}</div>
          <div><strong>Sector:</strong> {{ detailEntity.sector }}</div>
          <div><strong>Tipo:</strong> <span style="text-transform:capitalize">{{ detailEntity.tipo_usuario }}</span></div>
          <div><strong>Dirección:</strong> {{ detailEntity.direccion }}</div>
          <div><strong>Código usuario:</strong> {{ detailEntity.codigo_usuario }}</div>
        </template>
        <template v-else>
          <div><strong>Serial:</strong> {{ detailEntity.serial }}</div>
          <div><strong>Tipo:</strong> {{ detailEntity.tipo }}</div>
          <div><strong>Suscriptor:</strong> {{ mm.historial?.suscriptor_nombre || detailEntity.suscriptor_id || '—' }}</div>
          <div><strong>Dirección:</strong> {{ detailEntity.direccion }}</div>
          <div><strong>Instalación:</strong> {{ detailEntity.fecha_instalacion }}</div>
          <div><strong>Condición:</strong> <span class="badge" :class="condicionTone(detailEntity.condicion)" style="text-transform:capitalize">{{ detailEntity.condicion || 'bueno' }}</span></div>
          <div><strong>Estado:</strong> <span class="badge" :class="detailEntity.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ detailEntity.estado }}</span></div>
        </template>
      </div>

      <template v-if="detailIsSus">
        <h3 class="mt-2">Micromedidores</h3>
        <DataTable :columns="mmCols" :rows="mm.historial?.micromedidores || []" empty-text="Sin micromedidores asociados.">
          <template #cell="{ row, col }">
            <span v-if="col.key === 'suscriptor'">{{ mm.historial?.suscriptor?.nombre || row.suscriptor_nombre || '—' }}</span>
            <span v-else-if="col.key === 'condicion'"><span class="badge" :class="condicionTone(row.condicion)" style="text-transform:capitalize">{{ row.condicion || 'bueno' }}</span></span>
            <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
            <span v-else>{{ row[col.key] ?? '—' }}</span>
          </template>
        </DataTable>

        <div v-if="susMmOptions.length > 1" class="field mt-2">
          <label>Consultar lecturas por medidor</label>
          <SearchableSelect v-model="detailSusMmId" :options="susMmOptions" placeholder="Seleccione un medidor…" clearable />
        </div>
        <template v-if="detailSusMmId">
          <h3 class="mt-2">Lecturas</h3>
          <DataTable :columns="detailLecCols" :rows="detailLecturas" empty-text="Sin lecturas registradas para este medidor.">
            <template #cell="{ row, col }">
              <span v-if="col.num" :style="{ textAlign: col.align }">{{ fmtNum(row[col.key]) }}</span>
              <span v-else-if="col.key === 'tipo'"><span class="badge" :class="row.promedio_usado ? 'badge-info' : 'badge-muted'">{{ row.promedio_usado ? 'Estimada' : 'Física' }}</span></span>
              <span v-else-if="col.key === 'foto'">
                <img v-if="row.foto_url" :src="row.foto_url" class="mini-foto" alt="Evidencia" loading="lazy"
                  @click="verFoto(row.foto_url, `Lectura · ${row.fecha}`)" />
                <span v-else class="muted">—</span>
              </span>
              <span v-else>{{ row[col.key] ?? '—' }}</span>
            </template>
          </DataTable>
        </template>
        <p v-else-if="susMmOptions.length" class="muted mt-2">Seleccione un medidor para ver sus lecturas (no se mezclan las de varios medidores).</p>
      </template>

      <template v-else>
        <div class="mt-2" style="display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap">
          <div class="tabs" style="border-bottom:none; margin-bottom:0">
            <button :class="{ active: detailTab === 'lecturas' }" @click="detailTab = 'lecturas'"><AppIcon name="edit" :size="15" />Lecturas</button>
            <button :class="{ active: detailTab === 'grafico' }" @click="detailTab = 'grafico'"><AppIcon name="report" :size="15" />Gráfico últimas 6</button>
          </div>
          <div style="display:flex; gap:.5rem">
            <button v-if="detailTab === 'lecturas'" class="btn btn-ghost btn-sm" @click="abrirPrint"><AppIcon name="report" :size="16" />Imprimir mediciones</button>
            <button v-else class="btn btn-ghost btn-sm" @click="abrirPrintChart"><AppIcon name="report" :size="16" />Imprimir gráfico</button>
          </div>
        </div>

        <div v-if="detailTab === 'lecturas'">
          <p class="muted mb-1" style="font-size:.82rem">Promedio histórico de consumo: <strong>{{ promedioTexto }}</strong></p>
          <DataTable :columns="detailLecCols" :rows="detailLecturas" empty-text="Sin lecturas registradas.">
            <template #cell="{ row, col }">
              <span v-if="col.num" :style="{ textAlign: col.align }">{{ fmtNum(row[col.key]) }}</span>
              <span v-else-if="col.key === 'tipo'"><span class="badge" :class="row.promedio_usado ? 'badge-info' : 'badge-muted'">{{ row.promedio_usado ? 'Estimada' : 'Física' }}</span></span>
              <span v-else-if="col.key === 'foto'">
                <img v-if="row.foto_url" :src="row.foto_url" class="mini-foto" alt="Evidencia" loading="lazy"
                  @click="verFoto(row.foto_url, `Lectura · ${row.fecha}`)" />
                <span v-else class="muted">—</span>
              </span>
              <span v-else>{{ row[col.key] ?? '—' }}</span>
            </template>
          </DataTable>
        </div>

        <div v-else>
          <div class="chart-card">
            <div class="chart-head">
              <div>
                <h3 style="margin:0">Consumo — últimas 6 mediciones</h3>
                <p class="muted" style="margin:.15rem 0 0; font-size:.8rem">{{ chartPeriodo }} · Total: {{ fmtNum(totalUltimas6) }} m³</p>
              </div>
              <span class="badge badge-info">Prom. {{ promedioHistorico === null || promedioHistorico === undefined ? '—' : fmtNum(promedioHistorico) + ' m³' }}</span>
            </div>
            <div v-if="ultimas6.length" class="chart-body">
              <div class="chart-plot">
                <div class="chart-tracks-row">
                  <div
                    v-if="promedioHistorico !== null && promedioHistorico !== undefined && maxConsumoChart"
                    class="chart-avg"
                    :style="{ bottom: `${Math.max(0, Math.min(100, (Number(promedioHistorico) / maxConsumoChart) * 100))}%` }"
                    :title="`Promedio histórico: ${fmtNum(promedioHistorico)} m³`"
                  >
                    <span class="chart-avg-label">Prom. {{ fmtNum(promedioHistorico) }}</span>
                  </div>
                  <div v-for="l in ultimas6" :key="l.id" class="track-col">
                    <span class="bar-value">{{ l.consumoNum === null ? '—' : fmtNum(l.consumoNum) }}</span>
                    <div class="bar-track">
                      <div
                        class="bar-fill"
                        :class="l.promedio_usado ? 'is-est' : 'is-fis'"
                        :style="{ height: alturaBarra(l.consumoNum) + '%' }"
                        :title="`${l.fecha} · Consumo ${l.consumoNum === null ? '—' : fmtNum(l.consumoNum) + ' m³'} (${l.promedio_usado ? 'estimada' : 'física'})`"
                      ></div>
                    </div>
                  </div>
                </div>
                <div class="chart-labels-row">
                  <div v-for="l in ultimas6" :key="'lbl-' + l.id" class="label-col">
                    <span class="bar-mes">{{ l.mesCorto }}</span>
                    <span class="bar-fecha">{{ String(l.fecha).slice(5) }}</span>
                    <span class="bar-flag" :class="l.promedio_usado ? 'badge badge-info' : 'bar-flag-empty'">{{ l.promedio_usado ? 'Est.' : '' }}</span>
                  </div>
                </div>
              </div>
              <div class="chart-legend">
                <span class="lg"><i class="sw sw-fis"></i>Física</span>
                <span class="lg"><i class="sw sw-est"></i>Estimada (promedio)</span>
                <span class="lg"><i class="sw sw-avg"></i>Promedio histórico</span>
              </div>
              <p class="hint">Barras = consumo en m³ de cada medición ({{ chartPeriodo }}). La línea punteada es el promedio histórico validado ({{ promedioTexto }}).</p>
            </div>
            <p v-else class="muted mt-2">Sin lecturas para graficar.</p>
          </div>
        </div>
      </template>
    </BaseModal>

    <!-- MODAL IMPRIMIR MEDICIONES -->
    <BaseModal v-model="showPrint" title="Imprimir mediciones">
      <div class="form-row" style="margin-bottom:1rem">
        <div class="field"><label>Año *</label>
          <SearchableSelect v-model="printForm.anio" :options="aniosOptions" placeholder="Año" />
        </div>
        <div class="field"><label>Mes inicio</label>
          <SearchableSelect v-model="printForm.mes_inicio" :options="mesesOptions" placeholder="Enero" clearable />
        </div>
        <div class="field"><label>Mes fin</label>
          <SearchableSelect v-model="printForm.mes_fin" :options="mesesOptions" placeholder="Diciembre" clearable />
        </div>
      </div>
      <p class="muted" style="margin:0 0 .75rem">{{ printRows.length }} lectura(s) en el periodo {{ printPeriodo }} · Consumo total: {{ fmtNum(printTotal) }} m³ · Promedio histórico: {{ promedioTexto }}</p>

      <div class="print-area">
        <div class="print-head">
          <img class="print-logo print-logo-acr" src="/print-logo-acr.png" alt="ACR" />
          <div class="print-empresa">
            <h2>ACUEDUCTO COMUNITARIO BARRIO RICAURTE “ACUARICAURTE”</h2>
            <p>J.A.C. - COMISIÓN EMPRESARIAL · NIT: 809000633-7 · CEL: 3227928798</p>
          </div>
          <img class="print-logo print-logo-sup" src="/print-logo-superservicios.png" alt="Superservicios" />
        </div>
        <div class="print-title">Historial de mediciones del micromedidor</div>
        <table class="print-meta">
          <tr><th>Medidor (serial)</th><td>{{ detailEntity?.serial }}</td><th>Tipo</th><td>{{ detailEntity?.tipo || '—' }}</td></tr>
          <tr><th>Suscriptor</th><td>{{ mm.historial?.suscriptor_nombre || detailEntity?.suscriptor_id || '—' }}</td><th>Dirección</th><td>{{ detailEntity?.direccion || '—' }}</td></tr>
          <tr><th>Periodo</th><td>{{ printPeriodo }}</td><th>Condición</th><td style="text-transform:capitalize">{{ detailEntity?.condicion || 'bueno' }}</td></tr>
          <tr><th>Promedio histórico</th><td colspan="3"><strong>{{ promedioHistorico === null || promedioHistorico === undefined ? '— (sin consumos históricos)' : fmtNum(promedioHistorico) + ' m³' }}</strong> — promedio validado de los consumos de las últimas {{ promedioBaseN }} lectura(s) con consumo</td></tr>
        </table>
        <table class="print-table">
          <thead>
            <tr><th>Mes</th><th>Fecha</th><th>Lectura (m³)</th><th>Consumo (m³)</th><th>Novedad</th></tr>
          </thead>
          <tbody>
            <tr v-for="l in printRows" :key="l.id">
              <td>{{ l.mes }}</td>
              <td>{{ l.fecha }}</td>
              <td style="text-align:right">{{ fmtNum(l.lectura) }}</td>
              <td style="text-align:right">{{ fmtNum(l.consumo) }}</td>
              <td>{{ l.novedad || '' }}</td>
            </tr>
            <tr v-if="!printRows.length"><td colspan="5" style="text-align:center">Sin lecturas en el periodo seleccionado.</td></tr>
          </tbody>
          <tfoot>
            <tr>
              <th colspan="3" style="text-align:right">Consumo total del periodo</th>
              <th style="text-align:right">{{ fmtNum(printTotal) }}</th>
              <th></th>
            </tr>
            <tr>
              <th colspan="3" style="text-align:right">Promedio histórico de consumo</th>
              <th style="text-align:right">{{ promedioHistorico === null || promedioHistorico === undefined ? '—' : fmtNum(promedioHistorico) }}</th>
              <th style="font-weight:400; font-size:.75rem">m³ · base {{ promedioBaseN }} lectura(s)</th>
            </tr>
          </tfoot>
        </table>
        <div class="print-foot">
          <span>Acueducto Comunitario Acuaricaurte “Avanzando Juntos”</span>
          <span>Impreso el {{ new Date().toLocaleDateString() }}</span>
        </div>
      </div>

      <template #footer>
        <button class="btn btn-ghost" @click="showPrint = false">Cerrar</button>
        <button class="btn btn-primary" @click="imprimir"><AppIcon name="report" :size="16" />Imprimir</button>
      </template>
    </BaseModal>

    <!-- MODAL IMPRIMIR GRÁFICO (últimas 6 mediciones) -->
    <BaseModal v-model="showPrintChart" title="Imprimir gráfico — últimas 6 mediciones" size="640">
      <p class="muted" style="margin:0 0 .75rem">{{ ultimas6.length }} medición(es) · {{ chartPeriodo }} · Total: {{ fmtNum(totalUltimas6) }} m³ · Promedio: {{ promedioTexto }}</p>
      <div class="print-area">
        <div class="print-head">
          <img class="print-logo print-logo-acr" src="/print-logo-acr.png" alt="ACR" />
          <div class="print-empresa">
            <h2>ACUEDUCTO COMUNITARIO BARRIO RICAURTE “ACUARICAURTE”</h2>
            <p>J.A.C. - COMISIÓN EMPRESARIAL · NIT: 809000633-7 · CEL: 3227928798</p>
          </div>
          <img class="print-logo print-logo-sup" src="/print-logo-superservicios.png" alt="Superservicios" />
        </div>
        <div class="print-title">Consumo — últimas 6 mediciones del micromedidor</div>
        <table class="print-meta">
          <tr><th>Medidor (serial)</th><td>{{ detailEntity?.serial }}</td><th>Suscriptor</th><td>{{ mm.historial?.suscriptor_nombre || detailEntity?.suscriptor_id || '—' }}</td></tr>
          <tr><th>Periodo graficado</th><td>{{ chartPeriodo }}</td><th>Promedio histórico</th><td><strong>{{ promedioHistorico === null || promedioHistorico === undefined ? '—' : fmtNum(promedioHistorico) + ' m³' }}</strong> (base {{ promedioBaseN }})</td></tr>
        </table>
        <div class="chart-print-bars">
          <div v-for="l in ultimas6" :key="l.id" class="chart-print-col">
            <span class="chart-print-val">{{ l.consumoNum === null ? '—' : fmtNum(l.consumoNum) }}</span>
            <div class="chart-print-track">
              <div
                class="chart-print-fill"
                :class="l.promedio_usado ? 'is-est' : 'is-fis'"
                :style="{ height: alturaBarra(l.consumoNum) + '%' }"
              ></div>
            </div>
            <span class="chart-print-mes">{{ l.mesCorto }} {{ String(l.fecha).slice(2, 7) }}</span>
            <span class="chart-print-tipo">{{ l.promedio_usado ? 'Est.' : 'Fís.' }}</span>
          </div>
          <p v-if="!ultimas6.length" class="muted">Sin lecturas para graficar.</p>
        </div>
        <table class="print-table">
          <thead>
            <tr><th>Fecha</th><th>Lectura (m³)</th><th>Consumo (m³)</th><th>Tipo</th></tr>
          </thead>
          <tbody>
            <tr v-for="l in ultimas6" :key="l.id">
              <td>{{ l.fecha }}</td>
              <td style="text-align:right">{{ fmtNum(l.lectura) }}</td>
              <td style="text-align:right">{{ l.consumoNum === null ? '—' : fmtNum(l.consumoNum) }}</td>
              <td>{{ l.promedio_usado ? 'Estimada' : 'Física' }}</td>
            </tr>
            <tr v-if="!ultimas6.length"><td colspan="4" style="text-align:center">Sin lecturas.</td></tr>
          </tbody>
          <tfoot>
            <tr>
              <th style="text-align:right">Total 6 mediciones</th>
              <th></th>
              <th style="text-align:right">{{ fmtNum(totalUltimas6) }}</th>
              <th></th>
            </tr>
            <tr>
              <th style="text-align:right">Promedio histórico</th>
              <th></th>
              <th style="text-align:right">{{ promedioHistorico === null || promedioHistorico === undefined ? '—' : fmtNum(promedioHistorico) }}</th>
              <th style="font-weight:400; font-size:.75rem">m³ · base {{ promedioBaseN }}</th>
            </tr>
          </tfoot>
        </table>
        <div class="print-foot">
          <span>Acueducto Comunitario Acuaricaurte “Avanzando Juntos”</span>
          <span>Impreso el {{ new Date().toLocaleDateString() }}</span>
        </div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showPrintChart = false">Cerrar</button>
        <button class="btn btn-primary" @click="imprimir"><AppIcon name="report" :size="16" />Imprimir</button>
      </template>
    </BaseModal>

    <ConfirmModal v-model:show="confirmShow" :title="confirmTitle" :message="confirmMsg" confirm-text="Sí, inactivar" danger :loading="accionBusy" @confirm="doDel" />

    <VisorFoto v-model:show="visorShow" :src="visorSrc" :titulo="visorTitulo" />
  </div>
</template>

<style>
/* Impresión: solo se imprime el área de mediciones / gráfico, con el mismo
   membrete institucional de los PDF del backend (logos ACR + Superservicios). */
@media print {
  @page { size: letter; margin: 12mm; }
  body * { visibility: hidden !important; }
  .print-area, .print-area * { visibility: visible !important; }
  .print-area {
    position: absolute;
    left: 0; top: 0;
    width: 100%;
    padding: 0;
    font-family: Helvetica, Arial, sans-serif;
  }
  .print-head {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    border-bottom: 2px solid #2160AD; padding-bottom: .5rem; margin-bottom: .6rem;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  .print-logo-acr { width: 56px; height: auto; }
  .print-logo-sup { width: 92px; height: auto; }
  .print-empresa { flex: 1; text-align: center; }
  .print-empresa h2 { color: #1B2733; font-size: .82rem; margin: 0; letter-spacing: .01em; }
  .print-empresa p { color: #5B6B7B; font-size: .68rem; margin: .15rem 0 0; }
  .print-title { color: #2160AD; font-size: .95rem; font-weight: 700; margin: 0 0 .55rem; }
  .print-meta, .print-table { width: 100%; border-collapse: collapse; margin-bottom: .9rem; font-size: .74rem; }
  .print-meta th, .print-meta td { border: 1px solid #D6E2F2; padding: .3rem .5rem; text-align: left; }
  .print-meta th { background: #EEF2FB; width: 17%; color: #1A4E8C; }
  .print-table th, .print-table td { border: 1px solid #D6E2F2; padding: .32rem .5rem; }
  .print-table thead th {
    background: #2160AD; color: #fff; text-align: left;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  .print-table tbody tr:nth-child(even) { background: #EEF2FB; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .print-table tfoot th { background: #EEF2FB; color: #1B2733; }
  .print-foot {
    display: flex; justify-content: space-between; align-items: flex-end;
    margin-top: 1.4rem; padding-top: .4rem; border-top: 1px solid #D6E2F2;
    font-size: .7rem; color: #5B6B7B; font-style: italic;
  }
  .chart-print-bars {
    display: flex; align-items: flex-end; gap: .6rem;
    border: 1px solid #D6E2F2; border-radius: 6px; padding: .8rem .8rem .6rem; margin-bottom: 1rem;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
  }
  .chart-print-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: .2rem; }
  .chart-print-val { font-size: .75rem; font-weight: 700; }
  .chart-print-track {
    width: 100%; max-width: 56px; height: 140px;
    border: 1px solid #D6E2F2; border-radius: 4px 4px 0 0;
    display: flex; align-items: flex-end; background: #EEF2FB;
  }
  .chart-print-fill { width: 100%; border-radius: 3px 3px 0 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .chart-print-fill.is-fis { background: #2160AD; }
  .chart-print-fill.is-est { background: #E0A106; }
  .chart-print-mes { font-size: .7rem; font-weight: 600; }
  .chart-print-tipo { font-size: .68rem; color: #444; }
}
</style>

<style scoped>
.print-area { background: #fff; border: 1px dashed var(--acr-borde); border-radius: 8px; padding: 1rem; }
.print-head {
  display: flex; align-items: center; justify-content: space-between; gap: .8rem;
  border-bottom: 2px solid var(--acr-azul); padding-bottom: .5rem; margin-bottom: .6rem;
}
.print-logo-acr { width: 52px; height: auto; }
.print-logo-sup { width: 86px; height: auto; }
.print-empresa { flex: 1; text-align: center; }
.print-empresa h2 { color: var(--acr-texto); font-size: .8rem; margin: 0; letter-spacing: .01em; }
.print-empresa p { color: var(--acr-texto-suave); font-size: .66rem; margin: .15rem 0 0; }
.print-title { color: var(--acr-azul); font-size: .92rem; font-weight: 700; margin: 0 0 .55rem; }
.print-meta, .print-table { width: 100%; border-collapse: collapse; margin-bottom: .9rem; font-size: .76rem; }
.print-meta th, .print-meta td { border: 1px solid var(--acr-borde); padding: .3rem .5rem; text-align: left; }
.print-meta th { background: var(--acr-azul-50); width: 17%; color: var(--acr-azul-700); }
.print-table th, .print-table td { border: 1px solid var(--acr-borde); padding: .32rem .5rem; }
.print-table thead th { background: var(--acr-azul); color: #fff; text-align: left; }
.print-table tbody tr:nth-child(even) { background: var(--acr-azul-50); }
.print-table tfoot th { background: var(--acr-azul-50); color: var(--acr-texto); }
.print-foot {
  display: flex; justify-content: space-between; align-items: flex-end;
  margin-top: 1.2rem; padding-top: .4rem; border-top: 1px solid var(--acr-borde);
  font-size: .72rem; color: var(--acr-texto-suave); font-style: italic;
}

/* Gráfico últimas 6 mediciones */
.chart-card {
  background: linear-gradient(180deg, var(--acr-azul-50) 0%, #fff 42%);
  border: 1px solid var(--acr-borde); border-radius: 12px; padding: 1rem 1.1rem;
  box-shadow: var(--acr-sombra-sm); margin-top: .75rem;
}
.chart-head { display: flex; align-items: flex-start; justify-content: space-between; gap: .8rem; flex-wrap: wrap; margin-bottom: .6rem; }
.chart-body { margin-top: .4rem; }
.chart-plot { position: relative; padding-top: 1.5rem; }
.chart-tracks-row { position: relative; display: flex; align-items: flex-end; gap: .7rem; height: 200px; border-bottom: 2px solid var(--acr-borde); padding-bottom: 0; }
.track-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: .25rem; height: 100%; min-width: 0; }
.chart-labels-row { display: flex; gap: .7rem; padding-top: .45rem; }
.label-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: .15rem; min-width: 0; }
.bar-flag { font-size: .65rem; padding: .05rem .45rem; min-height: 1.05rem; line-height: 1; }
.bar-flag-empty { min-height: 1.05rem; }
.chart-avg {
  position: absolute; left: 0; right: 0; height: 0;
  border-top: 2px dashed var(--acr-bad); z-index: 2; pointer-events: none;
}
.chart-avg-label {
  position: absolute; right: 0; top: -1.35rem;
  background: var(--acr-bad-bg); color: var(--acr-bad);
  font-size: .7rem; font-weight: 700; padding: .1rem .5rem; border-radius: 999px;
  border: 1px solid #f1c2c2; white-space: nowrap;
}
.chart-bars { display: flex; align-items: flex-end; gap: .7rem; min-height: 210px; border-bottom: 2px solid var(--acr-borde); padding-bottom: .5rem; }
.bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: .25rem; min-width: 0; }
.bar-value { font-size: .8rem; font-weight: 800; color: var(--acr-azul-700); font-variant-numeric: tabular-nums; }
.bar-track {
  width: 100%; max-width: 64px; height: 160px;
  background: #EEF3FA; border: 1px solid var(--acr-borde); border-radius: 8px 8px 4px 4px;
  display: flex; align-items: flex-end; overflow: hidden;
}
.bar-fill { width: 100%; border-radius: 7px 7px 0 0; transition: height .3s; }
.bar-fill.is-fis { background: linear-gradient(180deg, #3A7BD0 0%, var(--acr-azul) 100%); }
.bar-fill.is-est {
  background: repeating-linear-gradient(135deg, #E0A106 0 8px, #C78F05 8px 16px);
}
.bar-mes { font-size: .75rem; font-weight: 700; text-transform: capitalize; }
.bar-fecha { font-size: .7rem; color: var(--acr-texto-suave); font-variant-numeric: tabular-nums; }
.bar-flag { font-size: .65rem; padding: .05rem .45rem; }
.chart-legend { display: flex; gap: 1rem; flex-wrap: wrap; margin: .7rem 0 .3rem; font-size: .78rem; color: var(--acr-texto-suave); }
.chart-legend .lg { display: inline-flex; align-items: center; gap: .35rem; }
.chart-legend .sw { width: 14px; height: 10px; border-radius: 3px; display: inline-block; }
.sw-fis { background: var(--acr-azul); }
.sw-est { background: repeating-linear-gradient(135deg, #E0A106 0 4px, #C78F05 4px 8px); border: 1px solid #C78F05; }
.sw-avg { height: 0 !important; width: 18px !important; border-top: 2px dashed var(--acr-bad); border-radius: 0 !important; }
.chart-card .hint { font-size: .72rem; color: var(--acr-texto-suave); margin: .3rem 0 0; }

/* Vista previa del gráfico dentro del modal de impresión */
.chart-print-bars {
  display: flex; align-items: flex-end; gap: .6rem;
  border: 1px solid var(--acr-borde); border-radius: 8px; padding: .8rem .8rem .6rem; margin-bottom: 1rem;
  background: #FBFDFF;
}
.chart-print-col { flex: 1; display: flex; flex-direction: column; align-items: center; gap: .2rem; }
.chart-print-val { font-size: .75rem; font-weight: 700; color: var(--acr-azul-700); }
.chart-print-track {
  width: 100%; max-width: 56px; height: 140px;
  border: 1px solid var(--acr-borde); border-radius: 6px 6px 3px 3px;
  display: flex; align-items: flex-end; background: #EEF3FA; overflow: hidden;
}
.chart-print-fill { width: 100%; }
.chart-print-fill.is-fis { background: var(--acr-azul); }
.chart-print-fill.is-est { background: #E0A106; }
.chart-print-mes { font-size: .7rem; font-weight: 600; }
.chart-print-tipo { font-size: .68rem; color: var(--acr-texto-suave); }
/* Miniaturas de evidencias en tablas */
.mini-foto { width: 56px; height: 42px; object-fit: cover; border-radius: 6px; border: 1px solid var(--acr-borde); cursor: zoom-in; }
.mini-foto:hover { border-color: var(--acr-azul); }
</style>
