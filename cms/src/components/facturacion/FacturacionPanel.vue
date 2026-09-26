<script setup>
import { computed, ref, watch } from 'vue'
import BaseAlert from '../BaseAlert.vue'
import AppIcon from '../AppIcon.vue'
import FacturacionResultado from './FacturacionResultado.vue'
import { apiError } from '../../api/http'
import { generarArchivoFacturacion, previsualizarFacturacion } from '../../api/facturacion'
import { useBusy } from '../../utils/async'

const meses = [
  { value: 1, label: 'Enero' }, { value: 2, label: 'Febrero' },
  { value: 3, label: 'Marzo' }, { value: 4, label: 'Abril' },
  { value: 5, label: 'Mayo' }, { value: 6, label: 'Junio' },
  { value: 7, label: 'Julio' }, { value: 8, label: 'Agosto' },
  { value: 9, label: 'Septiembre' }, { value: 10, label: 'Octubre' },
  { value: 11, label: 'Noviembre' }, { value: 12, label: 'Diciembre' },
]

function fechaISO(fecha) {
  const y = fecha.getFullYear()
  const m = String(fecha.getMonth() + 1).padStart(2, '0')
  const d = String(fecha.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

function periodoAnterior() {
  const ahora = new Date()
  return new Date(ahora.getFullYear(), ahora.getMonth() - 1, 1)
}

const inicial = periodoAnterior()
const mes = ref(inicial.getMonth() + 1)
const anio = ref(inicial.getFullYear())
const archivo = ref(null)
const inputArchivo = ref(null)
const preview = ref(null)
const error = ref('')
const exito = ref('')
const confirmarReemplazo = ref(false)
const { busy: previsualizando, run: runPreview } = useBusy()
const { busy: generando, run: runGenerate } = useBusy()

function rangoRecomendado(m, y) {
  const desde = new Date(y, m - 1, 25)
  const hasta = new Date(y, m, 5)
  return { desde: fechaISO(desde), hasta: fechaISO(hasta) }
}

const rangoInicial = rangoRecomendado(mes.value, anio.value)
const fechaDesde = ref(rangoInicial.desde)
const fechaHasta = ref(rangoInicial.hasta)
const mesLabel = computed(() => meses.find((m) => m.value === Number(mes.value))?.label || '')
const necesitaConfirmar = computed(() => Number(preview.value?.resumen?.celdas_mes_con_datos || 0) > 0)
const puedeGenerar = computed(() => Boolean(
  archivo.value && preview.value && !previsualizando.value && !generando.value &&
  (!necesitaConfirmar.value || confirmarReemplazo.value)
))

watch([mes, anio], () => {
  const rango = rangoRecomendado(Number(mes.value), Number(anio.value))
  fechaDesde.value = rango.desde
  fechaHasta.value = rango.hasta
  preview.value = null
  confirmarReemplazo.value = false
  exito.value = ''
})

watch([fechaDesde, fechaHasta], () => {
  preview.value = null
  confirmarReemplazo.value = false
  exito.value = ''
})

function elegirArchivo() { inputArchivo.value?.click() }

function alElegirArchivo(evento) {
  const seleccionado = evento.target.files?.[0] || null
  evento.target.value = ''
  error.value = ''
  exito.value = ''
  preview.value = null
  confirmarReemplazo.value = false
  if (!seleccionado) return
  if (!seleccionado.name.toLowerCase().endsWith('.xlsx')) {
    archivo.value = null
    error.value = 'Selecciona el formato de Excel .xlsx del sistema contable.'
    return
  }
  if (seleccionado.size > 20 * 1024 * 1024) {
    archivo.value = null
    error.value = 'El archivo supera el máximo de 20 MB.'
    return
  }
  archivo.value = seleccionado
}

function opciones() {
  return {
    mes: Number(mes.value),
    anio: Number(anio.value),
    fecha_desde: fechaDesde.value,
    fecha_hasta: fechaHasta.value,
  }
}

async function previsualizar() {
  error.value = ''
  preview.value = null
  confirmarReemplazo.value = false
  if (!archivo.value) { error.value = 'Selecciona el archivo Excel de facturación.'; return }
  if (!fechaDesde.value || !fechaHasta.value) { error.value = 'Selecciona el rango de fechas de las lecturas.'; return }
  await runPreview(async () => {
    try {
      preview.value = await previsualizarFacturacion(archivo.value, opciones())
    } catch (e) {
      error.value = apiError(e, 'No se pudo revisar el archivo.')
    }
  })
}

async function generar() {
  error.value = ''
  if (!puedeGenerar.value) return
  await runGenerate(async () => {
    try {
      await generarArchivoFacturacion(archivo.value, {
        ...opciones(),
        confirmar_reemplazo: confirmarReemplazo.value,
      })
      exito.value = `Se descargó la copia de ${mesLabel.value} ${anio.value}. El archivo original no se modificó.`
    } catch (e) {
      error.value = apiError(e, 'No se pudo generar el Excel. Revisa el archivo y vuelve a previsualizar.')
    }
  })
}

function csvSeguro(valor) {
  let texto = valor == null ? '' : String(valor)
  if (/^[\s]*[=+\-@]/.test(texto)) texto = `'${texto}`
  return `"${texto.replaceAll('"', '""')}"`
}

function descargarCsv(filas, nombre, columnas) {
  const lineas = [columnas.map(([, titulo]) => csvSeguro(titulo)).join(';')]
  for (const fila of filas || []) {
    lineas.push(columnas.map(([campo]) => csvSeguro(fila[campo])).join(';'))
  }
  const blob = new Blob([`\uFEFF${lineas.join('\r\n')}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = nombre
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

function descargarNovedades() {
  descargarCsv(preview.value?.novedades, `Novedades_Facturacion_${mes.value}_${anio.value}.csv`, [
    ['fila', 'Fila Excel'], ['area', 'Área'], ['nombre_excel', 'Usuario en Excel'],
    ['nmedidor_excel', 'Medidor en Excel'], ['tipo', 'Tipo de novedad'],
    ['serial_db', 'Medidor asociado en ACR'], ['fecha_lectura', 'Fecha lectura DB'],
    ['valor_excel', 'Valor anterior Excel'], ['valor_sugerido', 'Valor sugerido'], ['detalle', 'Detalle'],
  ])
}

function descargarAuditoria() {
  descargarCsv(preview.value?.auditoria, `Detalle_Facturacion_${mes.value}_${anio.value}.csv`, [
    ['fila', 'Fila Excel'], ['area', 'Área'], ['nombre_excel', 'Usuario en Excel'],
    ['codigo_db', 'Código usuario ACR'], ['nombre_db', 'Usuario ACR'],
    ['nmedidor_excel', 'Medidor en Excel'], ['serial_usado_db', 'Medidor usado ACR'],
    ['origen_valor', 'Origen del valor'], ['fecha_lectura_db', 'Fecha lectura DB'],
    ['valor_excel_original', 'Valor original'], ['valor_generado', 'Valor generado'],
    ['estado_fila', 'Estado'], ['novedades', 'Notas'],
  ])
}
</script>

<template>
  <section class="fact-panel">
    <div class="fact-intro">
      <h2>Preparar archivo de facturación</h2>
      <p class="muted">Sube el formato del sistema contable, elige el mes y el rango de lecturas. Se genera una copia nueva; no se crean ni modifican lecturas en ACR.</p>
    </div>

    <BaseAlert v-if="error" type="bad" class="mb-1">{{ error }}</BaseAlert>
    <BaseAlert v-if="exito" type="ok" class="mb-1">{{ exito }}</BaseAlert>

    <div class="fact-form">
      <div class="field fact-archivo">
        <label>Archivo Excel (.xlsx) *</label>
        <input ref="inputArchivo" class="fact-file-hidden" type="file" accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" @change="alElegirArchivo" />
        <div class="fact-file-line">
          <button type="button" class="btn btn-ghost" :disabled="previsualizando || generando" @click="elegirArchivo">Elegir archivo</button>
          <span class="fact-file-name" :class="{ muted: !archivo }">{{ archivo?.name || 'Ningún archivo seleccionado' }}</span>
        </div>
      </div>

      <div class="form-row fact-periodo">
        <div class="field"><label>Mes a facturar *</label>
          <select v-model.number="mes" class="input">
            <option v-for="item in meses" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
        </div>
        <div class="field"><label>Año *</label>
          <input v-model.number="anio" class="input" type="number" min="2000" max="2100" />
        </div>
        <div class="field"><label>Lecturas desde *</label>
          <input v-model="fechaDesde" class="input" type="date" />
        </div>
        <div class="field"><label>Lecturas hasta *</label>
          <input v-model="fechaHasta" class="input" type="date" />
        </div>
      </div>
      <p class="hint">Rango recomendado: día 25 del mes a facturar hasta día 5 del siguiente. Puedes ajustarlo según las fechas reales de toma.</p>

      <div class="fact-actions">
        <button class="btn btn-primary" type="button" :disabled="!archivo || previsualizando || generando" @click="previsualizar">
          <span v-if="previsualizando" class="spinner"></span>
          <AppIcon v-else name="eye" />
          {{ previsualizando ? 'Revisando archivo…' : 'Previsualizar' }}
        </button>
        <button class="btn btn-ghost" type="button" :disabled="!puedeGenerar" @click="generar">
          <span v-if="generando" class="spinner"></span>
          <AppIcon v-else name="download" />
          {{ generando ? 'Generando Excel…' : 'Descargar Excel completado' }}
        </button>
      </div>
    </div>

    <div v-if="preview" class="fact-preview-box">
      <FacturacionResultado
        :resultado="preview"
        @descargar-novedades="descargarNovedades"
        @descargar-auditoria="descargarAuditoria"
      />
      <label v-if="necesitaConfirmar" class="fact-confirmar">
        <input v-model="confirmarReemplazo" type="checkbox" />
        Confirmo reemplazar {{ preview.resumen.celdas_mes_con_datos }} celdas que ya traen un valor distinto de cero en {{ mesLabel }} dentro de la copia que se descargará. El archivo original no cambia.
      </label>
    </div>
  </section>
</template>

<style scoped>
.fact-panel { display: grid; gap: 1rem; }
.fact-intro h2 { margin: 0 0 .2rem; font-size: 1.15rem; }
.fact-intro p { margin: 0; }
.fact-form { border: 1px solid var(--acr-borde); border-radius: var(--acr-radio); background: #fff; padding: 1rem; }
.fact-file-hidden { position: absolute; width: 1px; height: 1px; opacity: 0; pointer-events: none; }
.fact-file-line { display: flex; align-items: center; gap: .7rem; flex-wrap: wrap; }
.fact-file-name { overflow-wrap: anywhere; font-size: .88rem; }
.fact-periodo { margin-top: .9rem; }
.fact-actions { display: flex; flex-wrap: wrap; gap: .55rem; margin-top: .9rem; }
.fact-preview-box { border: 1px solid var(--acr-borde); border-radius: var(--acr-radio); background: #fff; padding: 1rem; }
.fact-confirmar { display: flex; align-items: flex-start; gap: .55rem; margin-top: 1rem; padding: .75rem; border: 1px solid #e8bd5a; border-radius: var(--acr-radio-sm); background: #fff8e4; color: #72520b; font-size: .88rem; }
.fact-confirmar input { margin-top: .15rem; accent-color: var(--acr-azul); }
@media (max-width: 700px) { .fact-form { padding: .75rem; } }
</style>
