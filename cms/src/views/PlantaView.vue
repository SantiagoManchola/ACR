<script setup>
import { onMounted, ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePlantaStore } from '../stores/planta'
import { useInventarioStore } from '../stores/inventario'
import { useUsuariosStore } from '../stores/usuarios'
import { useAuthStore } from '../stores/auth'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import FotoEvidencia from '../components/FotoEvidencia.vue'
import VisorFoto from '../components/VisorFoto.vue'
import BaseInput from '../components/BaseInput.vue'
import GraficoHoras from '../components/GraficoHoras.vue'
import { apiError, descargarReporte } from '../api/http'
import { fmtNum, fmtRango, hoyColombia, formatoOptions } from '../utils/format'
import { debounce } from '../utils/debounce'
import { useBusy } from '../utils/async'

const planta = usePlantaStore()
const inv = useInventarioStore()
const usu = useUsuariosStore()
const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const tab = ref('parametros')
/* Sincronía pestaña ↔ URL: /planta/parametros, /planta/mediciones, … */
const TABS_VALIDOS = ['parametros', 'mediciones', 'fuera', 'productos', 'dosificaciones', 'actividades', 'horas']
watch(() => route.params.tab, (t) => {
  if (t === undefined) return
  if (!TABS_VALIDOS.includes(t)) { router.replace({ name: 'planta', params: { tab: tab.value } }); return }
  if (t !== tab.value) tab.value = t
}, { immediate: true })
function setTab(t) {
  tab.value = t
  router.replace({ name: 'planta', params: { tab: t } })
}
const saving = ref(false)
/* Cargas de botones asíncronos: deshabilitados hasta resolver la petición */
const { busy: repBusy, run: repRun } = useBusy()
const { busy: refrescando, run: refRun } = useBusy()
// El operario NO puede hacer CRUD de parámetros ni crear/editar químicos:
// solo registra INGRESOS (entradas) de químicos YA EXISTENTES en la planta.
// El backend lo restringe a químicos EN planta (403 en otro caso).
const esOperario = computed(() => auth.rol === 'operario')
const puedeGestionarUsuarios = computed(() => ['admin', 'administrativo'].includes(auth.rol))

const paramMap = computed(() => Object.fromEntries(planta.parametros.map((p) => [p.id, p])))
const userOptions = computed(() => (usu.opciones.length ? usu.opciones : planta.usuariosOpciones).map((u) => ({ value: u.id, label: u.nombre })))
const paramOptions = computed(() => planta.parametros.map((p) => ({ value: p.id, label: p.nombre })))

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

/* Ubicación "Planta de tratamiento": los químicos de este módulo son SOLO los
   de esa sede (ni disponibilidad ni descuentos de otras ubicaciones). */
const plantaUbi = computed(() => {
  const us = inv.ubicaciones || []
  // Coincidencia exacta primero: "Planta de tratamiento" antes que "Planta".
  return us.find((u) => (u.nombre || '').toLowerCase() === 'planta de tratamiento')
    || us.find((u) => (u.nombre || '').toLowerCase() === 'planta')
    || us.find((u) => /planta/i.test(u.nombre || '')) || null
})
const quimicosPlanta = computed(() => {
  if (!plantaUbi.value) return []
  return inv.quimicos
    .map((q) => {
      const fila = (q.stock || []).find((s) => s.ubicacion_id === plantaUbi.value.id)
      return fila ? { ...q, cantidad: fila.cantidad, stockPlantaId: fila.id } : null
    })
    .filter(Boolean)
})
const quimicosBajos = computed(() => quimicosPlanta.value.filter((q) => q.minimo != null && Number(q.cantidad) <= Number(q.minimo)).length)

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

/* Filtros por pestaña (fechas por defecto: hoy en Colombia; auto-búsqueda con debounce) */
/* Página y orden de cada tabla (paginación y orden server-side) */
const pageMed = ref(1)
const pageAct = ref(1)
const pageDosis = ref(1)
const pageHora = ref(1)
const ordenMed = ref(''); const dirMed = ref('desc')
const ordenAct = ref(''); const dirAct = ref('desc')
const ordenDosis = ref(''); const dirDosis = ref('desc')
const ordenHora = ref(''); const dirHora = ref('desc')

const medFiltro = ref({ parametro_id: '', fuera_rango: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function filtrarMed() { planta.loadMediciones(buildFiltros(medFiltro.value), pageMed.value, ordenMed.value, dirMed.value) }

const actFiltro = ref({ tipo: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function filtrarAct() { planta.loadActividades(buildFiltros(actFiltro.value), pageAct.value, ordenAct.value, dirAct.value) }

const dosisFiltro = ref({ elemento_id: '', fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function filtrarDosis() { planta.loadDosificaciones(buildFiltros(dosisFiltro.value), pageDosis.value, ordenDosis.value, dirDosis.value) }

const horaFiltro = ref({ fecha_inicio: hoyColombia(), fecha_fin: hoyColombia() })
function filtrarHora() { planta.loadHoras(buildFiltros(horaFiltro.value), pageHora.value, ordenHora.value, dirHora.value) }

watch(medFiltro, debounce(() => { pageMed.value = 1; filtrarMed() }, 350), { deep: true })
watch(actFiltro, debounce(() => { pageAct.value = 1; filtrarAct() }, 350), { deep: true })
watch(dosisFiltro, debounce(() => { pageDosis.value = 1; filtrarDosis() }, 350), { deep: true })
watch(horaFiltro, debounce(() => { pageHora.value = 1; filtrarHora() }, 350), { deep: true })
function irPaginaMed(p) { pageMed.value = p; filtrarMed() }
function irPaginaAct(p) { pageAct.value = p; filtrarAct() }
function irPaginaDosis(p) { pageDosis.value = p; filtrarDosis() }
function irPaginaHora(p) { pageHora.value = p; filtrarHora() }
function ordenarMed({ key, dir }) { ordenMed.value = key; dirMed.value = dir; pageMed.value = 1; filtrarMed() }
function ordenarAct({ key, dir }) { ordenAct.value = key; dirAct.value = dir; pageAct.value = 1; filtrarAct() }
function ordenarDosis({ key, dir }) { ordenDosis.value = key; dirDosis.value = dir; pageDosis.value = 1; filtrarDosis() }
function ordenarHora({ key, dir }) { ordenHora.value = key; dirHora.value = dir; pageHora.value = 1; filtrarHora() }

const fueraRangoOptions = [
  { value: 'true', label: 'Sí' },
  { value: 'false', label: 'No' },
]
const tipoAguaOptions = [
  { value: 'cruda', label: 'Cruda' },
  { value: 'tratada', label: 'Tratada' },
]

function refrescar() { return refRun(refreshPlanta) }
function refreshPlanta() {
  const tareas = [
    planta.loadParametros(), inv.loadCategorias(), inv.loadQuimicos(), inv.loadUbicaciones(),
    filtrarMed(), filtrarAct(), filtrarDosis(), filtrarHora(),
    planta.loadFueraRango(),
  ]
  if (puedeGestionarUsuarios.value) tareas.push(usu.loadOpciones())
  return Promise.all(tareas)
}

/* Parámetros */
const showParam = ref(false)
const editingParam = ref(null)
const paramError = ref('')
const emptyParam = () => ({ nombre: '', tipo_agua: 'cruda', unidad: '', valor_min: '', valor_max: '' })
const paramForm = ref(emptyParam())
const paramCols = [
  { key: 'nombre', label: 'Parámetro', cardTitle: true },
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
const emptyMed = () => ({ parametro_id: null, valor: '', accion_correctiva: '', observaciones: '', foto_url: '' })
const medForm = ref(emptyMed())
const fotoMedRef = ref(null)
const medCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'parametro', label: 'Parámetro', cardTitle: true, sortValue: (r) => r.parametro_nombre || '' },
  { key: 'tipo_agua', label: 'Tipo de agua', hideOnCard: true, sortValue: (r) => paramMap.value[r.parametro_id]?.tipo_agua || '' },
  { key: 'valor', label: 'Valor', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad', sortValue: (r) => paramMap.value[r.parametro_id]?.unidad || '' },
  { key: 'responsable', label: 'Responsable', sortValue: (r) => r.responsable_nombre || '' },
  { key: 'fuera_rango', label: 'Estado' },
  { key: 'foto', label: 'Foto', sortable: false },
  { key: 'accion_correctiva', label: 'Acción correctiva', wide: true },
]
/* Pestaña "Fuera de rango": estado ACTUAL por parámetro (última medición) */
const fueraCols = [
  { key: 'parametro', label: 'Parámetro', cardTitle: true },
  { key: 'tipo_agua', label: 'Tipo de agua', hideOnCard: true },
  { key: 'valor', label: 'Último valor', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'rango', label: 'Rango' },
  { key: 'fecha', label: 'Desde' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'accion_correctiva', label: 'Acción correctiva', wide: true },
]
function openNewMed() { medForm.value = emptyMed(); medError.value = ''; showMed.value = true }
async function saveMed() {
  medError.value = ''
  if (!medForm.value.parametro_id || medForm.value.valor === '') { medError.value = 'Parámetro y valor son obligatorios.'; return }
  if (fotoMedRef.value?.ocupado()) { medError.value = 'Espera a que termine de subir la foto.'; return }
  saving.value = true
  try {
    await planta.createMedicion({
      parametro_id: Number(medForm.value.parametro_id),
      valor: Number(medForm.value.valor),
      accion_correctiva: medForm.value.accion_correctiva || null,
      observaciones: medForm.value.observaciones || null,
      foto_url: medForm.value.foto_url || null,
    })
    showMed.value = false; await Promise.all([filtrarMed(), planta.loadFueraRango()])
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
const prodOptionsDisp = computed(() => quimicosPlanta.value.map((p) => ({
  value: p.id, label: `${p.nombre} (${fmtNum(p.cantidad)} ${p.unidad || ''} en planta)`.trim(),
})))
const dosisUnidad = computed(() => {
  const p = inv.quimicos.find((x) => x.id === dosisForm.value.elemento_id)
  return p?.unidad || ''
})
const prodCols = [
  { key: 'nombre', label: 'Insumo', cardTitle: true },
  { key: 'unidad', label: 'Unidad', hideOnCard: true },
  { key: 'cantidad', label: 'Disponible en planta', align: 'right', num: true },
  { key: 'minimo', label: 'Mínimo', align: 'right' },
  { key: 'estado', label: 'Estado' },
]
const dosisCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'insumo', label: 'Insumo', cardTitle: true, sortValue: (r) => prodMap.value[r.elemento_id] || '' },
  { key: 'tasa', label: 'Tasa (bomba)' },
  { key: 'cantidad', label: 'Aplicado', align: 'right', num: true },
  { key: 'unidad', label: 'Unidad' },
  { key: 'observaciones', label: 'Observaciones', wide: true },
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
    if (editingProd.value) {
      // El stock se ajusta por entradas/salidas/traslados desde Inventario,
      // no editando la ficha del químico.
      await inv.updateQuimico(editingProd.value.id, {
        nombre: prodForm.value.nombre,
        categoria_id: Number(prodForm.value.categoria_id),
        unidad: prodForm.value.unidad || null,
        minimo: prodForm.value.minimo === '' ? null : Number(prodForm.value.minimo),
      })
    } else {
      // El químico se crea con su stock inicial EN LA PLANTA
      await inv.createQuimico({
        nombre: prodForm.value.nombre,
        categoria_id: Number(prodForm.value.categoria_id),
        unidad: prodForm.value.unidad || null,
        minimo: prodForm.value.minimo === '' ? null : Number(prodForm.value.minimo),
        ubicacion_id: plantaUbi.value ? Number(plantaUbi.value.id) : null,
        cantidad_inicial: prodForm.value.cantidad === '' ? 0 : Number(prodForm.value.cantidad),
      })
    }
    showProd.value = false; await inv.loadQuimicos()
  } catch (e) { prodError.value = apiError(e) } finally { saving.value = false }
}
/* Ingreso de químicos YA EXISTENTES (entradas de stock en planta).
   El operario NO crea fichas nuevas: registra que ingresaron X unidades de
   un químico existente. El backend exige químico EN planta (403 si no). */
const showIng = ref(false)
const ingError = ref('')
const ingForm = ref({ elemento_id: null, nombre: '', cantidad: '', motivo: '', observaciones: '' })
function openIngreso(r) {
  ingForm.value = { elemento_id: r.id, nombre: r.nombre, cantidad: '', motivo: '', observaciones: '' }
  ingError.value = ''; showIng.value = true
}
async function saveIngreso() {
  ingError.value = ''
  if (!ingForm.value.cantidad || Number(ingForm.value.cantidad) <= 0) { ingError.value = 'Ingrese una cantidad mayor a 0.'; return }
  if (!plantaUbi.value) { ingError.value = 'No se encontró la ubicación Planta de tratamiento.'; return }
  saving.value = true
  try {
    await inv.registrarMovimiento(ingForm.value.elemento_id, 'entrada', {
      ubicacion_id: Number(plantaUbi.value.id),
      cantidad: Number(ingForm.value.cantidad),
      motivo: ingForm.value.motivo || null,
      observaciones: ingForm.value.observaciones || null,
      fecha: hoyColombia(),
    })
    showIng.value = false; await inv.loadQuimicos()
  } catch (e) { ingError.value = apiError(e) } finally { saving.value = false }
}
function openNewDosis() { dosisForm.value = emptyDosis(); dosisError.value = ''; showDosis.value = true }
async function saveDosis() {
  dosisError.value = ''
  if (!dosisForm.value.elemento_id || !dosisForm.value.cantidad) { dosisError.value = 'Insumo y cantidad incorporada son obligatorios.'; return }
  saving.value = true
  try {
    await planta.createDosificacion({
      elemento_id: Number(dosisForm.value.elemento_id),
      // Cantidad INCORPORADA (ej. 1 L): esto descuenta del inventario EN PLANTA
      cantidad: Number(dosisForm.value.cantidad),
      ubicacion_id: plantaUbi.value ? Number(plantaUbi.value.id) : null,
      // Tasa de la bomba (ej. ml/min): solo informativa, NO descuenta
      tasa: dosisForm.value.tasa === '' ? null : Number(dosisForm.value.tasa),
      unidad_tasa: dosisForm.value.unidad_tasa || 'ml/min',
      observaciones: dosisForm.value.observaciones || null,
    })
     showDosis.value = false; await Promise.all([filtrarDosis(), inv.loadQuimicos()])
  } catch (e) { dosisError.value = apiError(e) } finally { saving.value = false }
}

/* Resumen "¿para cuánto me queda químico?": por cada químico dosificado en
   planta, stock restante EN PLANTA + horas de dosificación continua a la
   última tasa usada. */
const resumenDosis = computed(() => {
  const map = {}
  for (const d of planta.dosificaciones) { // vienen desc por fecha
    const q = quimicosPlanta.value.find((x) => x.id === d.elemento_id)
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

/* Gráfico de horas de servicio: componente reutilizable (también en el Dashboard).
   Ver components/GraficoHoras.vue — anual → mes → semana, escala 0–24 en días. */
const graficoHorasRef = ref(null)
function filtrarTablaPorDia(fecha) {
  // Día clickeado en el gráfico: filtra la tabla de abajo a esa fecha (Limpiar lo revierte).
  horaFiltro.value = { fecha_inicio: fecha, fecha_fin: fecha }
  filtrarHora()
  document.querySelector('.report-bar')?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

/* Actividades */
const showAct = ref(false)
const actError = ref('')
const emptyAct = () => ({ tipo: '', responsable_id: null, observaciones: '', evidencia: '', foto_url: '' })
const actForm = ref(emptyAct())
const fotoActRef = ref(null)
const actCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora', hideOnCard: true },
  { key: 'tipo', label: 'Tipo', cardTitle: true },
  { key: 'responsable', label: 'Responsable', sortValue: (r) => r.responsable_nombre || '' },
  { key: 'estado', label: 'Estado' },
  { key: 'observaciones', label: 'Observaciones', wide: true },
  { key: 'evidencia', label: 'Evidencia', wide: true },
  { key: 'foto', label: 'Foto', sortable: false },
]
const actTipos = ['Limpieza', 'Desinfección', 'Tanques', 'Bocatoma', 'Mantenimiento']
const actTiposOptions = computed(() => actTipos.map((t) => ({ value: t, label: t })))
function openNewAct() { actForm.value = emptyAct(); actError.value = ''; showAct.value = true }
async function saveAct() {
  actError.value = ''
  if (!actForm.value.tipo) { actError.value = 'El tipo de actividad es obligatorio.'; return }
  if (fotoActRef.value?.ocupado()) { actError.value = 'Espera a que termine de subir la foto.'; return }
  saving.value = true
  try {
    await planta.createActividad({
      ...actForm.value,
      responsable_id: actForm.value.responsable_id ? Number(actForm.value.responsable_id) : null,
      foto_url: actForm.value.foto_url || null,
    })
    showAct.value = false; await filtrarAct()
  } catch (e) { actError.value = apiError(e) } finally { saving.value = false }
}

/* Horas */
const showHora = ref(false)
const horaError = ref('')
const emptyHora = () => ({ fecha: new Date().toISOString().slice(0, 10), horas: '', responsable_id: null, observaciones: '' })
const horaForm = ref(emptyHora())
const horaCols = [
  { key: 'fecha', label: 'Fecha', cardTitle: true },
  { key: 'horas', label: 'Horas', align: 'right', num: true },
  { key: 'observaciones', label: 'Observaciones', wide: true },
]
function openNewHora() { horaForm.value = emptyHora(); horaError.value = ''; showHora.value = true }
async function saveHora() {
  horaError.value = ''
  if (!horaForm.value.horas) { horaError.value = 'Ingrese las horas de servicio.'; return }
  saving.value = true
  try { await planta.createHoraServicio({ fecha: horaForm.value.fecha || new Date().toISOString().slice(0, 10), horas: Number(horaForm.value.horas), responsable_id: horaForm.value.responsable_id ? Number(horaForm.value.responsable_id) : null, observaciones: horaForm.value.observaciones || null });     showHora.value = false; await filtrarHora(); graficoHorasRef.value?.recargar() }
  catch (e) { horaError.value = apiError(e) } finally { saving.value = false }
}

onMounted(() => {
  /* Cargas en paralelo desde el primer render (sin awaits previos que
     dejen las tablas en "Sin información") */
  filtrarMed()
  filtrarAct()
  filtrarDosis()
  filtrarHora()
  planta.loadParametros()
  inv.loadCategorias()
  inv.loadQuimicos()
  inv.loadUbicaciones()
  planta.loadFueraRango()
  planta.loadUsuariosOpciones()
  if (puedeGestionarUsuarios.value) usu.loadOpciones()
})

/* Al entrar a cada pestaña se refrescan sus datos para no mostrar información desactualizada
   (punto 5: los químicos se actualizan al registrar dosificaciones / al abrir la pestaña). */
watch(tab, (t) => {
  if (t === 'productos') inv.loadQuimicos()
  else if (t === 'dosificaciones') filtrarDosis()
  else if (t === 'mediciones') filtrarMed()
  else if (t === 'fuera') planta.loadFueraRango()
  else if (t === 'actividades') filtrarAct()
  else if (t === 'horas') filtrarHora()
})
</script>

<template>
  <div class="view-fit">
    <h1>Planta de tratamiento</h1>
    <p class="muted">Parámetros, mediciones, dosificaciones, actividades y horas de servicio.</p>

    <div class="toolbar" style="margin-bottom:1rem">
      <button class="btn btn-ghost" :disabled="refrescando" @click="refrescar"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
    </div>

    <div class="tabs">
      <button :class="{ active: tab === 'parametros' }" @click="setTab('parametros')"><AppIcon name="flask" />Parámetros</button>
      <button :class="{ active: tab === 'mediciones' }" @click="setTab('mediciones')"><AppIcon name="drop" />Mediciones</button>
      <button :class="{ active: tab === 'fuera' }" @click="setTab('fuera')">
        <AppIcon name="alert" />Fuera de rango
        <span v-if="planta.fueraRango.length" class="badge badge-bad">{{ planta.fueraRango.length }}</span>
      </button>
      <button :class="{ active: tab === 'productos' }" @click="setTab('productos')"><AppIcon name="flask" />Químicos
        <span v-if="quimicosBajos" class="badge badge-bad">{{ quimicosBajos }}</span>
      </button>
      <button :class="{ active: tab === 'dosificaciones' }" @click="setTab('dosificaciones')"><AppIcon name="package" />Dosificaciones</button>
      <button :class="{ active: tab === 'actividades' }" @click="setTab('actividades')"><AppIcon name="wrench" />Actividades</button>
      <button :class="{ active: tab === 'horas' }" @click="setTab('horas')"><AppIcon name="clock" />Horas de servicio</button>
    </div>

    <!-- PARÁMETROS -->
    <div v-if="tab === 'parametros'" class="tab-panel">
      <div class="toolbar"><button v-if="!esOperario" class="btn btn-primary" @click="openNewParam"><AppIcon name="plus" />Nuevo parámetro</button></div>
      <DataTable :columns="paramCols" :rows="planta.parametros" :loading="planta.loading" empty-text="Sin parámetros configurados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo_agua'" style="text-transform:capitalize">{{ row.tipo_agua }}</span>
          <span v-else-if="col.key === 'rango'">{{ fmtRango(row.valor_min, row.valor_max) }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button v-if="!esOperario" class="btn btn-ghost btn-sm" @click="openEditParam(row)"><AppIcon name="edit" :size="16" /></button>
        </template>
      </DataTable>
    </div>

    <!-- MEDICIONES -->
    <div v-else-if="tab === 'mediciones'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Parámetro</label>
          <SearchableSelect v-model="medFiltro.parametro_id" :options="paramOptions" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Fuera de rango</label>
          <SearchableSelect v-model="medFiltro.fuera_rango" :options="fueraRangoOptions" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Desde</label><BaseInput v-model="medFiltro.fecha_inicio" type="date" /></div>
        <div class="field"><label>Hasta</label><BaseInput v-model="medFiltro.fecha_fin" type="date" /></div>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewMed"><AppIcon name="plus" />Registrar medición</button></div>
      <DataTable
        :columns="medCols" :rows="planta.mediciones" :loading="planta.loading"
        :total="planta.medicionesTotal" :page="pageMed" :page-size="20"
        :sort-by="ordenMed" :sort-dir="dirMed"
        empty-text="Sin mediciones registradas."
        @update:page="irPaginaMed"
        @update:sort="ordenarMed"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'parametro'">{{ row.parametro_nombre || paramMap[row.parametro_id]?.nombre || row.parametro_id }}</span>
          <span v-else-if="col.key === 'tipo_agua'" style="text-transform:capitalize">{{ paramMap[row.parametro_id]?.tipo_agua || '—' }}</span>
          <span v-else-if="col.key === 'responsable'">{{ row.responsable_nombre || '—' }}</span>
          <span v-else-if="col.key === 'unidad'">{{ paramMap[row.parametro_id]?.unidad || '—' }}</span>
          <span v-else-if="col.key === 'fuera_rango'"><span class="badge" :class="row.fuera_rango ? 'badge-bad' : 'badge-ok'">{{ row.fuera_rango ? 'Fuera de rango' : 'En rango' }}</span></span>
          <span v-else-if="col.key === 'foto'">
            <img v-if="row.foto_url" :src="row.foto_url" class="mini-foto" alt="Evidencia" loading="lazy"
              @click="verFoto(row.foto_url, `${paramMap[row.parametro_id]?.nombre || 'Medición'} · ${row.fecha}`)" />
            <span v-else class="muted">—</span>
          </span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('mediciones', medFiltro))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- FUERA DE RANGO (estado actual por parámetro) -->
    <div v-else-if="tab === 'fuera'" class="tab-panel">
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

    <!-- INSUMOS / QUÍMICOS (solo stock de la planta) -->
    <div v-else-if="tab === 'productos'" class="tab-panel">
      <BaseAlert v-if="!plantaUbi" type="warn" class="mb-1">
        No se encontró la ubicación «Planta de tratamiento» (Inventario → Ubicaciones). Créala para gestionar los químicos de la planta.
      </BaseAlert>
      <p class="muted" v-else>Mostrando únicamente la disponibilidad de químicos en <strong>{{ plantaUbi.nombre }}</strong>.</p>
      <div class="toolbar">
        <button v-if="!esOperario" class="btn btn-primary" @click="openNewProd" :disabled="!plantaUbi"><AppIcon name="plus" />Nuevo químico</button>
        <button class="btn btn-ghost" :disabled="refrescando" @click="refrescar"><span v-if="refrescando" class="spinner"></span><AppIcon v-else name="refresh" />{{ refrescando ? 'Actualizando…' : 'Refrescar' }}</button>
      </div>
      <DataTable :columns="prodCols" :rows="quimicosPlanta" :loading="inv.loading" empty-text="Sin químicos registrados en la planta.">
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
          <button v-if="!esOperario" class="btn btn-ghost btn-sm" @click="openEditProd(row)" title="Editar"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openIngreso(row)" title="Registrar ingreso"><AppIcon name="plus" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('quimicos', {}))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- DOSIFICACIONES -->
    <div v-else-if="tab === 'dosificaciones'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Insumo</label>
          <SearchableSelect v-model="dosisFiltro.elemento_id" :options="prodOptionsDisp" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Desde</label><BaseInput v-model="dosisFiltro.fecha_inicio" type="date" /></div>
        <div class="field"><label>Hasta</label><BaseInput v-model="dosisFiltro.fecha_fin" type="date" /></div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewDosis"><AppIcon name="plus" />Registrar dosificación</button>
        <button v-if="!esOperario" class="btn btn-ghost" @click="openNewProd"><AppIcon name="package" />Nuevo químico</button>
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
      <DataTable
        :columns="dosisCols" :rows="planta.dosificaciones" :loading="planta.loading"
        :total="planta.dosificacionesTotal" :page="pageDosis" :page-size="20"
        :sort-by="ordenDosis" :sort-dir="dirDosis"
        empty-text="Sin dosificaciones registradas."
        @update:page="irPaginaDosis"
        @update:sort="ordenarDosis"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'insumo'">{{ row.elemento_nombre || prodMap[row.elemento_id] || row.elemento_id }}</span>
          <span v-else-if="col.key === 'tasa'">{{ row.tasa != null ? `${fmtNum(row.tasa)} ${row.unidad_tasa || 'ml/min'}` : '—' }}</span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('dosificaciones', dosisFiltro))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- ACTIVIDADES -->
    <div v-else-if="tab === 'actividades'" class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Tipo</label>
          <SearchableSelect v-model="actFiltro.tipo" :options="actTiposOptions" placeholder="Todos" clearable />
        </div>
        <div class="field"><label>Desde</label><BaseInput v-model="actFiltro.fecha_inicio" type="date" /></div>
        <div class="field"><label>Hasta</label><BaseInput v-model="actFiltro.fecha_fin" type="date" /></div>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewAct"><AppIcon name="plus" />Registrar actividad</button></div>
      <DataTable
        :columns="actCols" :rows="planta.actividades" :loading="planta.loading"
        :total="planta.actividadesTotal" :page="pageAct" :page-size="20"
        :sort-by="ordenAct" :sort-dir="dirAct"
        empty-text="Sin actividades registradas."
        @update:page="irPaginaAct"
        @update:sort="ordenarAct"
      >
        <template #cell="{ row, col }">
          <span v-if="col.key === 'responsable'">{{ row.responsable_nombre || '—' }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else-if="col.key === 'tipo'" style="text-transform:capitalize">{{ row.tipo }}</span>
          <span v-else-if="col.key === 'foto'">
            <img v-if="row.foto_url" :src="row.foto_url" class="mini-foto" alt="Evidencia" loading="lazy"
              @click="verFoto(row.foto_url, `${row.tipo} · ${row.fecha}`)" />
            <span v-else class="muted">—</span>
          </span>
          <span v-else-if="col.num">{{ fmtNum(row[col.key]) }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <label>Formato</label>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('actividades', actFiltro))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- HORAS -->
    <div v-else class="tab-panel">
      <div class="filter-bar">
        <div class="field"><label>Desde</label><BaseInput v-model="horaFiltro.fecha_inicio" type="date" /></div>
        <div class="field"><label>Hasta</label><BaseInput v-model="horaFiltro.fecha_fin" type="date" /></div>
      </div>
      <div class="toolbar"><button class="btn btn-primary" @click="openNewHora"><AppIcon name="plus" />Registrar horas</button></div>

      <GraficoHoras ref="graficoHorasRef" @click-dia="filtrarTablaPorDia" />

      <DataTable
        :columns="horaCols" :rows="planta.horas" :loading="planta.loading"
        :total="planta.horasTotal" :page="pageHora" :page-size="20"
        :sort-by="ordenHora" :sort-dir="dirHora"
        empty-text="Sin horas de servicio registradas."
        @update:page="irPaginaHora"
        @update:sort="ordenarHora"
      />
      <div class="report-bar">
        <label>Formato</label>
        <SearchableSelect v-model="formatoReporte" :options="formatoOptions" placeholder="Formato" style="width:auto;min-width:130px" />
        <button class="btn btn-ghost" :disabled="repBusy" @click="repRun(() => generarReporte('horas', horaFiltro))"><span v-if="repBusy" class="spinner"></span><AppIcon v-else name="download" />{{ repBusy ? 'Generando…' : 'Generar reporte' }}</button>
      </div>
    </div>

    <!-- MODALES -->
    <BaseModal v-model="showParam" :title="editingParam ? 'Editar parámetro' : 'Nuevo parámetro'">
      <BaseAlert v-if="paramError" type="bad" class="mb-1">{{ paramError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="paramForm.nombre" placeholder="Ej. pH, cloro residual, turbiedad" /></div>
        <div class="field"><label>Tipo de agua</label>
          <SearchableSelect v-model="paramForm.tipo_agua" :options="tipoAguaOptions" placeholder="Tipo de agua" />
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
      <FotoEvidencia ref="fotoMedRef" v-model="medForm.foto_url" modulo="medicion" />
      <template #footer>
        <button class="btn btn-ghost" @click="showMed = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving || fotoMedRef?.subiendo" @click="saveMed">
          <span v-if="fotoMedRef?.subiendo" class="spinner"></span>{{ fotoMedRef?.subiendo ? 'Subiendo foto…' : (saving ? 'Guardando…' : 'Guardar') }}
        </button>
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
        <div class="field"><label>Cantidad inicial (en planta)</label><input class="input" type="number" step="0.01" v-model="prodForm.cantidad" placeholder="0" :disabled="!!editingProd" /></div>
        <div class="field"><label>Stock mínimo (alerta)</label><input class="input" type="number" step="0.01" v-model="prodForm.minimo" placeholder="0" /></div>
      </div>
      <p class="hint" v-if="editingProd">El stock se ajusta con entradas, salidas y traslados desde Inventario, no editando la ficha.</p>
      <p class="hint" v-else>El stock inicial se registra en la ubicación «{{ plantaUbi?.nombre || 'Planta de tratamiento' }}».</p>
      <template #footer>
        <button class="btn btn-ghost" @click="showProd = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveProd">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showIng" title="Registrar ingreso de químico">
      <BaseAlert v-if="ingError" type="bad" class="mb-1">{{ ingError }}</BaseAlert>
      <p class="muted">Químico existente: <strong>{{ ingForm.nombre }}</strong> · Se ingresa en <strong>{{ plantaUbi?.nombre || 'Planta de tratamiento' }}</strong>.</p>
      <div class="form-row">
        <div class="field"><label>Cantidad *</label><input class="input" type="number" step="0.01" v-model="ingForm.cantidad" placeholder="0" /></div>
        <div class="field"><label>Motivo</label><input class="input" v-model="ingForm.motivo" placeholder="Ej. compra, donación" /></div>
      </div>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="ingForm.observaciones"></textarea></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showIng = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveIngreso">{{ saving ? 'Guardando…' : 'Registrar ingreso' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showDosis" title="Registrar dosificación">      <BaseAlert v-if="dosisError" type="bad" class="mb-1">{{ dosisError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Insumo *</label>
          <SearchableSelect v-model="dosisForm.elemento_id" :options="prodOptionsDisp" placeholder="Seleccione un químico/insumo…" />
        </div>
        <div class="field"><label>Cantidad incorporada *</label><input class="input" type="number" step="0.01" v-model="dosisForm.cantidad" placeholder="Ej. 1" /></div>
        <div class="field"><label>Tasa de dosificación</label><input class="input" type="number" step="0.1" v-model="dosisForm.tasa" placeholder="Ej. 5" /></div>
        <div class="field"><label>Unidad de tasa</label><input class="input" v-model="dosisForm.unidad_tasa" placeholder="ml/min" /></div>
      </div>
      <p class="hint" v-if="dosisUnidad">Unidad del insumo: <strong>{{ dosisUnidad }}</strong>.</p>
      <p class="hint">La <strong>cantidad incorporada</strong> (ej. 1 L de cloro) <strong>descuenta del stock en «{{ plantaUbi?.nombre || 'Planta de tratamiento' }}»</strong> — el de otras sedes no se toca. La <strong>tasa</strong> (ej. ml/min de la bomba) es solo informativa: sirve para estimar cuánto tiempo dura el químico puesto en el tanque.</p>
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
          <SearchableSelect v-model="actForm.tipo" :options="actTiposOptions" placeholder="Seleccione…" clearable />
        </div>
        <div class="field" style="grid-column:span 2"><label>Responsable</label>
          <SearchableSelect v-model="actForm.responsable_id" :options="userOptions" placeholder="Usuario responsable" clearable />
        </div>
      </div>
      <div class="field"><label>Observaciones</label><textarea class="textarea" v-model="actForm.observaciones"></textarea></div>
      <div class="field"><label>Evidencia (referencia)</label><input class="input" v-model="actForm.evidencia" placeholder="Ej. código de foto, folio" /></div>
      <FotoEvidencia ref="fotoActRef" v-model="actForm.foto_url" modulo="actividad" />
      <template #footer>
        <button class="btn btn-ghost" @click="showAct = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving || fotoActRef?.subiendo" @click="saveAct">
          <span v-if="fotoActRef?.subiendo" class="spinner"></span>{{ fotoActRef?.subiendo ? 'Subiendo foto…' : (saving ? 'Guardando…' : 'Guardar') }}
        </button>
      </template>
    </BaseModal>

    <BaseModal v-model="showHora" title="Registrar horas de servicio">
      <BaseAlert v-if="horaError" type="bad" class="mb-1">{{ horaError }}</BaseAlert>
      <div class="form-row">
        <div class="field"><label>Fecha *</label><BaseInput v-model="horaForm.fecha" type="date" /></div>
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

    <VisorFoto v-model:show="visorShow" :src="visorSrc" :titulo="visorTitulo" />
  </div>
</template>

<style scoped>
/* Miniaturas de evidencias en tablas */
.mini-foto { width: 56px; height: 42px; object-fit: cover; border-radius: 6px; border: 1px solid var(--acr-borde); cursor: zoom-in; }
.mini-foto:hover { border-color: var(--acr-azul); }
</style>
