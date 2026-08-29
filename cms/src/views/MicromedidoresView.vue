<script setup>
import { onMounted, ref, computed } from 'vue'
import { useMicromedidoresStore } from '../stores/micromedidores'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import { apiError, descargarReporte } from '../api/http'
import { fmtNum } from '../utils/format'

const mm = useMicromedidoresStore()
const tab = ref('suscriptores')

const susMap = computed(() => Object.fromEntries(mm.suscriptores.map((s) => [s.id, s.nombre])))
const susOptions = computed(() => mm.suscriptores.map((s) => ({ value: s.id, label: s.nombre })))
const mmOptions = computed(() => mm.micromedidores.map((m) => ({ value: m.id, label: m.serial })))
const sectorOptions = computed(() => mm.sectores.map((s) => ({ value: s, label: s })))

const tipoUsuarioOptions = [
  { value: 'residencial', label: 'Residencial' },
  { value: 'comercial', label: 'Comercial' },
  { value: 'otro', label: 'Otro' },
]

/* Confirmación de acciones destructivas */
const confirmShow = ref(false)
const confirmTitle = ref('')
const confirmMsg = ref('')
const pendingDel = ref(null)
function askDel(tipo, r) {
  pendingDel.value = { tipo, id: r.id }
  if (tipo === 'sus') { confirmTitle.value = 'Inactivar suscriptor'; confirmMsg.value = `¿Inactivar al suscriptor «${r.nombre}»?` }
  else { confirmTitle.value = 'Inactivar micromedidor'; confirmMsg.value = `¿Inactivar el micromedidor «${r.serial}»?` }
  confirmShow.value = true
}
async function doDel() {
  const p = pendingDel.value
  confirmShow.value = false
  if (!p) return
  if (p.tipo === 'sus') { await mm.deleteSuscriptor(p.id); await mm.loadSuscriptores() }
  else { await mm.deleteMicromedidor(p.id); await mm.loadMicromedidores() }
  pendingDel.value = null
}
function refreshAll() { return Promise.all([mm.loadSuscriptores(), mm.loadMicromedidores(), mm.loadLecturas()]) }

/* ---------------- Filtros ---------------- */
const filtrosSus = ref({ nombre: '', identificacion: '', sector: '', tipo_usuario: '' })
const filtrosMm = ref({ serial: '', suscriptor_id: '', sector: '' })
const filtrosLec = ref({ sector: '', fecha_inicio: '', fecha_fin: '' })

function limpiarFiltrosSus() { filtrosSus.value = { nombre: '', identificacion: '', sector: '', tipo_usuario: '' }; mm.loadSuscriptores() }
function limpiarFiltrosMm() { filtrosMm.value = { serial: '', suscriptor_id: '', sector: '' }; mm.loadMicromedidores() }
function limpiarFiltrosLec() { filtrosLec.value = { sector: '', fecha_inicio: '', fecha_fin: '' }; mm.loadLecturas() }

function soloNoVacios(obj) {
  const out = {}
  for (const [k, v] of Object.entries(obj)) if (v !== '' && v !== null && v !== undefined) out[k] = v
  return out
}
function buscarSus() { mm.loadSuscriptores(soloNoVacios(filtrosSus.value)) }
function buscarMm() { mm.loadMicromedidores(soloNoVacios(filtrosMm.value)) }
function buscarLec() { mm.loadLecturas(soloNoVacios(filtrosLec.value)) }

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
function openDetailSus(r) { mm.loadHistorialSuscriptor(r.id); showDetail.value = true }
function openDetailMm(r) { mm.loadHistorialMicromedidor(r.id); showDetail.value = true }

/* ---------------- Suscriptores ---------------- */
const showSus = ref(false)
const editingSus = ref(null)
const susError = ref('')
const saving = ref(false)
const emptySus = () => ({ nombre: '', identificacion: '', codigo_usuario: '', codigo_facturacion: '', tipo_usuario: 'residencial', sector: '', direccion: '' })
const susForm = ref(emptySus())

const susCols = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'identificacion', label: 'Identificación' },
  { key: 'sector', label: 'Sector' },
  { key: 'tipo_usuario', label: 'Tipo' },
  { key: 'estado', label: 'Estado' },
  { key: 'direccion', label: 'Dirección' },
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
    showSus.value = false; await mm.loadSuscriptores()
  } catch (e) { susError.value = apiError(e) } finally { saving.value = false }
}
async function delSus(r) { askDel('sus', r) }
async function reactivarSus(r) {
  await mm.updateSuscriptor(r.id, { estado: 'activo' })
  await mm.loadSuscriptores()
}

/* ---------------- Micromedidores ---------------- */
const showMm = ref(false)
const editingMm = ref(null)
const mmError = ref('')
const emptyMm = () => ({ serial: '', tipo: '', suscriptor_id: null, direccion: '', fecha_instalacion: '' })
const mmForm = ref(emptyMm())

const mmCols = [
  { key: 'serial', label: 'Serial' },
  { key: 'tipo', label: 'Tipo' },
  { key: 'suscriptor', label: 'Suscriptor' },
  { key: 'direccion', label: 'Dirección' },
  { key: 'fecha_instalacion', label: 'Instalación' },
]
function openNewMm() { editingMm.value = null; mmForm.value = emptyMm(); mmError.value = ''; showMm.value = true }
function openEditMm(r) { editingMm.value = r; mmForm.value = { ...r }; mmError.value = ''; showMm.value = true }
async function saveMm() {
  mmError.value = ''
  if (!mmForm.value.serial) { mmError.value = 'El serial es obligatorio.'; return }
  saving.value = true
  try {
    if (editingMm.value) await mm.updateMicromedidor(editingMm.value.id, mmForm.value)
    else await mm.createMicromedidor(mmForm.value)
    showMm.value = false; await mm.loadMicromedidores()
  } catch (e) { mmError.value = apiError(e) } finally { saving.value = false }
}
async function delMm(r) { askDel('mm', r) }

/* ---------------- Lecturas ---------------- */
const showLec = ref(false)
const lecError = ref('')
const emptyLec = () => ({ micromedidor_id: null, suscriptor_id: null, lectura: '', novedad: '', irregular: false })
const lecForm = ref(emptyLec())

const lecCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'suscriptor', label: 'Suscriptor' },
  { key: 'micromedidor_id', label: 'Medidor' },
  { key: 'lectura', label: 'Lectura', align: 'right' },
  { key: 'consumo', label: 'Consumo', align: 'right' },
  { key: 'promedio', label: 'Promedio' },
  { key: 'irregular', label: 'Estado' },
  { key: 'novedad', label: 'Novedad' },
]
const detailLecCols = [
  { key: 'fecha', label: 'Fecha' },
  { key: 'hora', label: 'Hora' },
  { key: 'entidad', label: 'Suscriptor / Medidor' },
  { key: 'lectura', label: 'Lectura', align: 'right', num: true },
  { key: 'consumo', label: 'Consumo', align: 'right', num: true },
  { key: 'irregular', label: 'Irregular' },
  { key: 'novedad', label: 'Novedad' },
]
const detailIsSus = computed(() => !!mm.historial && !!mm.historial.suscriptor)
const detailEntity = computed(() => mm.historial?.suscriptor || mm.historial?.micromedidor || null)
const detailLecturas = computed(() => (mm.historial?.lecturas || []).map((l) => ({
  ...l,
  entidad: detailIsSus.value ? (susMap.value[l.suscriptor_id] || l.suscriptor_id) : (l.micromedidor_id),
})))
function onPickMedidor(val) {
  const id = val ?? lecForm.value.micromedidor_id
  const m = mm.micromedidores.find((x) => x.id === id)
  if (m && m.suscriptor_id) lecForm.value.suscriptor_id = m.suscriptor_id
}
function openNewLec() { lecForm.value = emptyLec(); lecError.value = ''; showLec.value = true }
async function saveLec() {
  lecError.value = ''
  if (!lecForm.value.micromedidor_id || !lecForm.value.suscriptor_id || lecForm.value.lectura === '') { lecError.value = 'Medidor, suscriptor y lectura son obligatorios.'; return }
  saving.value = true
  try {
    await mm.createLectura({
      micromedidor_id: Number(lecForm.value.micromedidor_id),
      suscriptor_id: Number(lecForm.value.suscriptor_id),
      lectura: Number(lecForm.value.lectura),
      novedad: lecForm.value.novedad || null,
      irregular: !!lecForm.value.irregular,
    })
    showLec.value = false; await mm.loadLecturas()
  } catch (e) { lecError.value = apiError(e) } finally { saving.value = false }
}

onMounted(async () => {
  await mm.loadSuscriptores()
  await mm.loadMicromedidores()
  await mm.loadLecturas()
  await mm.loadSectores()
})
</script>

<template>
  <div>
    <h1>Micromedidores</h1>
    <p class="muted">Suscriptores, medidores y lecturas (RF-21 a RF-36).</p>
    <BaseAlert v-if="repError" type="bad" class="mb-1">{{ repError }}</BaseAlert>

    <div class="tabs">
      <button :class="{ active: tab === 'suscriptores' }" @click="tab = 'suscriptores'"><AppIcon name="users" />Suscriptores</button>
      <button :class="{ active: tab === 'micromedidores' }" @click="tab = 'micromedidores'"><AppIcon name="gauge" />Micromedidores</button>
      <button :class="{ active: tab === 'lecturas' }" @click="tab = 'lecturas'"><AppIcon name="edit" />Lecturas</button>
    </div>

    <!-- SUSCRIPTORES -->
    <div v-if="tab === 'suscriptores'">
      <div class="filter-bar">
        <div class="field"><label>Nombre</label><input class="input" v-model="filtrosSus.nombre" /></div>
        <div class="field"><label>Identificación</label><input class="input" v-model="filtrosSus.identificacion" /></div>
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosSus.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Tipo de usuario</label>
          <SearchableSelect v-model="filtrosSus.tipo_usuario" :options="tipoUsuarioOptions" placeholder="Todos" clearable />
        </div>
        <div class="field" style="justify-content:flex-end">
          <button class="btn btn-primary" @click="buscarSus"><AppIcon name="search" />Filtrar</button>
          <button class="btn btn-ghost" @click="limpiarFiltrosSus"><AppIcon name="x" />Limpiar</button>
        </div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewSus"><AppIcon name="plus" />Nuevo suscriptor</button>
        <button class="btn btn-ghost" @click="refreshAll"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="susCols" :rows="mm.suscriptores" :loading="mm.loading" empty-text="Sin suscriptores.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'tipo_usuario'" style="text-transform:capitalize">{{ row.tipo_usuario }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditSus(row)"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openDetailSus(row)"><AppIcon name="eye" :size="16" /></button>
          <button v-if="row.estado === 'activo'" class="btn btn-ghost btn-sm" @click="delSus(row)" title="Inactivar"><AppIcon name="trash" :size="16" /></button>
          <button v-else class="btn btn-ghost btn-sm" @click="reactivarSus(row)" title="Activar"><AppIcon name="refresh" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <span class="muted">Reporte de suscriptores:</span>
        <select class="select" v-model="formatoReporte">
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
          <option value="pdf">PDF</option>
        </select>
        <button class="btn btn-ghost" @click="generarReporte('suscriptores')"><AppIcon name="download" />Generar reporte</button>
      </div>
    </div>

    <!-- MICROMEDIDORES -->
    <div v-else-if="tab === 'micromedidores'">
      <div class="filter-bar">
        <div class="field"><label>Serial</label><input class="input" v-model="filtrosMm.serial" /></div>
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosMm.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Suscriptor</label>
          <SearchableSelect v-model="filtrosMm.suscriptor_id" :options="susOptions" placeholder="Todos" clearable />
        </div>
        <div class="field" style="justify-content:flex-end">
          <button class="btn btn-primary" @click="buscarMm"><AppIcon name="search" />Filtrar</button>
          <button class="btn btn-ghost" @click="limpiarFiltrosMm"><AppIcon name="x" />Limpiar</button>
        </div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewMm"><AppIcon name="plus" />Nuevo micromedidor</button>
        <button class="btn btn-ghost" @click="refreshAll"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="mmCols" :rows="mm.micromedidores" :loading="mm.loading" empty-text="Sin micromedidores.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'suscriptor'">{{ susMap[row.suscriptor_id] || '—' }}</span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditMm(row)"><AppIcon name="edit" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="openDetailMm(row)"><AppIcon name="eye" :size="16" /></button>
          <button class="btn btn-ghost btn-sm" @click="delMm(row)"><AppIcon name="trash" :size="16" /></button>
        </template>
      </DataTable>
      <div class="report-bar">
        <span class="muted">Reporte de micromedidores:</span>
        <select class="select" v-model="formatoReporte">
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
          <option value="pdf">PDF</option>
        </select>
        <button class="btn btn-ghost" @click="generarReporte('micromedidores')"><AppIcon name="download" />Generar reporte</button>
      </div>
    </div>

    <!-- LECTURAS -->
    <div v-else-if="tab === 'lecturas'">
      <div class="filter-bar">
        <div class="field"><label>Sector</label>
          <SearchableSelect v-model="filtrosLec.sector" :options="sectorOptions" placeholder="Todos los sectores" clearable />
        </div>
        <div class="field"><label>Fecha inicio</label><input class="input" type="date" v-model="filtrosLec.fecha_inicio" /></div>
        <div class="field"><label>Fecha fin</label><input class="input" type="date" v-model="filtrosLec.fecha_fin" /></div>
        <div class="field" style="justify-content:flex-end">
          <button class="btn btn-primary" @click="buscarLec"><AppIcon name="search" />Filtrar</button>
          <button class="btn btn-ghost" @click="limpiarFiltrosLec"><AppIcon name="x" />Limpiar</button>
        </div>
      </div>
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewLec"><AppIcon name="plus" />Registrar lectura</button>
        <button class="btn btn-ghost" @click="refreshAll"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="lecCols" :rows="mm.lecturas" :loading="mm.loading" empty-text="Sin lecturas registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'suscriptor'">{{ susMap[row.suscriptor_id] || row.suscriptor_id }}</span>
          <span v-else-if="col.key === 'promedio'"><span class="badge" :class="row.promedio_usado ? 'badge-info' : 'badge-muted'">{{ row.promedio_usado ? 'Promedio' : 'Real' }}</span></span>
          <span v-else-if="col.key === 'irregular'"><span class="badge" :class="row.irregular ? 'badge-warn' : 'badge-ok'">{{ row.irregular ? 'Irregular' : 'OK' }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
      <div class="report-bar">
        <span class="muted">Reporte de lecturas:</span>
        <select class="select" v-model="formatoReporte">
          <option value="csv">CSV</option>
          <option value="xlsx">XLSX</option>
          <option value="pdf">PDF</option>
        </select>
        <button class="btn btn-ghost" @click="generarReporte('lecturas')"><AppIcon name="download" />Generar reporte</button>
      </div>
    </div>

    <!-- MODAL SUSCRIPTOR -->
    <BaseModal v-model="showSus" :title="editingSus ? 'Editar suscriptor' : 'Nuevo suscriptor'">
      <BaseAlert v-if="susError" type="bad" class="mb-1">{{ susError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="susForm.nombre" /></div>
        <div class="field"><label>Identificación</label><input class="input" v-model="susForm.identificacion" /></div>
        <div class="field"><label>Tipo de usuario</label>
          <select class="select" v-model="susForm.tipo_usuario">
            <option value="residencial">Residencial</option>
            <option value="comercial">Comercial</option>
            <option value="otro">Otro</option>
          </select>
        </div>
        <div class="field"><label>Sector / barrio</label>
          <SearchableSelect v-model="susForm.sector" :options="sectorOptions" placeholder="Seleccione o escriba un sector" clearable />
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

    <!-- MODAL MICROMEDIDOR -->
    <BaseModal v-model="showMm" :title="editingMm ? 'Editar micromedidor' : 'Nuevo micromedidor'">
      <BaseAlert v-if="mmError" type="bad" class="mb-1">{{ mmError }}</BaseAlert>
      <div class="form-row">
        <div class="field"><label>Serial *</label><input class="input" v-model="mmForm.serial" /></div>
        <div class="field"><label>Tipo</label><input class="input" v-model="mmForm.tipo" placeholder="Ej. analógico, digital" /></div>
        <div class="field" style="grid-column:span 2"><label>Suscriptor</label>
          <SearchableSelect v-model="mmForm.suscriptor_id" :options="susOptions" placeholder="Sin asignar" clearable />
        </div>
        <div class="field" style="grid-column:span 2"><label>Dirección</label><input class="input" v-model="mmForm.direccion" /></div>
        <div class="field"><label>Fecha de instalación</label><input class="input" type="date" v-model="mmForm.fecha_instalacion" /></div>
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
        <div class="field" style="grid-column:span 2"><label>Micromedidor *</label>
          <SearchableSelect v-model="lecForm.micromedidor_id" :options="mmOptions" placeholder="Seleccione…" @update:model-value="onPickMedidor" />
        </div>
        <div class="field" style="grid-column:span 2"><label>Suscriptor *</label>
          <SearchableSelect v-model="lecForm.suscriptor_id" :options="susOptions" placeholder="Seleccione…" />
        </div>
        <div class="field"><label>Lectura (m³) *</label><input class="input" type="number" step="1" placeholder="0" v-model="lecForm.lectura" /></div>
      </div>
      <div class="field">
        <label class="flex center gap-1" style="font-weight:600;cursor:pointer">
          <input type="checkbox" v-model="lecForm.irregular" /> Marcar como lectura estimada (sin medición física / usar promedio histórico)
        </label>
        <p class="hint">Según el procedimiento de Acuaricaurte, ante la falta de lectura se usa el promedio histórico (RF-02/RF-31).</p>
      </div>
      <div class="field">
        <label>Novedad</label>
        <textarea class="textarea" v-model="lecForm.novedad" placeholder="Observación o novedad de la lectura"></textarea>
      </div>
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
          <div><strong>Suscriptor:</strong> {{ susMap[detailEntity.suscriptor_id] || detailEntity.suscriptor_id }}</div>
          <div><strong>Dirección:</strong> {{ detailEntity.direccion }}</div>
          <div><strong>Instalación:</strong> {{ detailEntity.fecha_instalacion }}</div>
          <div><strong>Estado:</strong> {{ detailEntity.estado }}</div>
        </template>
      </div>

      <template v-if="detailIsSus">
        <h3 class="mt-2">Micromedidores</h3>
        <DataTable :columns="mmCols" :rows="mm.historial?.micromedidores || []" empty-text="Sin micromedidores asociados.">
          <template #cell="{ row, col }">
            <span v-if="col.key === 'suscriptor'">{{ susMap[row.suscriptor_id] || '—' }}</span>
            <span v-else>{{ row[col.key] ?? '—' }}</span>
          </template>
        </DataTable>
      </template>

      <h3 class="mt-2">Lecturas</h3>
      <DataTable :columns="detailLecCols" :rows="detailLecturas" empty-text="Sin lecturas registradas.">
        <template #cell="{ row, col }">
          <span v-if="col.num" :style="{ textAlign: col.align }">{{ fmtNum(row[col.key]) }}</span>
          <span v-else-if="col.key === 'irregular'"><span class="badge" :class="row.irregular ? 'badge-warn' : 'badge-ok'">{{ row.irregular ? 'Sí' : 'No' }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
      </DataTable>
    </BaseModal>

    <ConfirmModal v-model:show="confirmShow" :title="confirmTitle" :message="confirmMsg" confirm-text="Sí, inactivar" danger @confirm="doDel" />
  </div>
</template>
