<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePlantaStore } from '../stores/planta'
import AppIcon from './AppIcon.vue'
import SearchableSelect from './SearchableSelect.vue'
import { fmtNum, hoyColombia } from '../utils/format'

/* Gráfico de horas de servicio navegable anual → mes → semana.
   Se usa igual en Planta (Horas de servicio) y en el Dashboard.
   Emite `click-dia` con la fecha al pulsar una barra de día. */
const props = defineProps({
  textoAccionDia: { type: String, default: 'filtrar la tabla a ese día' },
})
const emit = defineEmits(['click-dia'])

const planta = usePlantaStore()

/* Escala fija 0–24 h en la vista por días (un día no pasa de 24 h); en vistas
   agregadas (meses/semanas) la escala se ajusta al máximo con ticks "bonitos".
   Cada barra es clickeable para bajar de nivel; el breadcrumb permite subir. */
const MESES_NOMBRE = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const vistaHora = ref('anual') // anual | mes | semana
const gAnio = ref(Number(hoyColombia().slice(0, 4)))
const gMes = ref(Number(hoyColombia().slice(5, 7)))
const gSem = ref(1)
const anioCargado = ref(null)
const graficoCargando = ref(false)
async function cargarAnio() {
  graficoCargando.value = true
  try { await planta.loadHorasGrafico({ fecha_inicio: `${gAnio.value}-01-01`, fecha_fin: `${gAnio.value}-12-31` }); anioCargado.value = gAnio.value }
  finally { graficoCargando.value = false }
}
function recargar() { return cargarAnio() }
function diasDelMes(anio, mes) { return new Date(anio, mes, 0).getDate() }
// Semanas del mes en bloques 1–7, 8–14, 15–21, 22–fin (4 por mes).
function rangoSemana(anio, mes, sem) {
  const fin = diasDelMes(anio, mes)
  const ini = sem === 1 ? 1 : sem === 2 ? 8 : sem === 3 ? 15 : 22
  return { ini, fin: sem === 4 ? fin : ini + 6 }
}
const pad2 = (n) => String(n).padStart(2, '0')
const fechaDe = (anio, mes, dia) => `${anio}-${pad2(mes)}-${pad2(dia)}`
// Agregados del año cargado: { 'YYYY-MM-DD': { horas, n } }
const horasMapa = computed(() => {
  const map = {}
  for (const h of (planta.horasGrafico || [])) {
    const f = String(h.fecha).slice(0, 10)
    const cur = map[f] || { horas: 0, n: 0 }
    cur.horas += Number(h.horas || 0); cur.n += 1
    map[f] = cur
  }
  return map
})
// Barras según el nivel: [{ id, etiqueta, sub, horas, n, titulo }]
const barrasHora = computed(() => {
  const out = []
  if (vistaHora.value === 'anual') {
    for (let m = 1; m <= 12; m++) {
      let horas = 0, n = 0
      const fin = diasDelMes(gAnio.value, m)
      for (let d = 1; d <= fin; d++) {
        const r = horasMapa.value[fechaDe(gAnio.value, m, d)]
        if (r) { horas += r.horas; n += r.n }
      }
      out.push({ id: `m${m}`, etiqueta: MESES_NOMBRE[m - 1].slice(0, 3), sub: String(gAnio.value).slice(2), horas, n, titulo: `${MESES_NOMBRE[m - 1]} ${gAnio.value}: ${fmtNum(horas)} h · ${n} registro(s). Clic para ver las semanas.` })
    }
  } else if (vistaHora.value === 'mes') {
    for (let s = 1; s <= 4; s++) {
      const { ini, fin } = rangoSemana(gAnio.value, gMes.value, s)
      let horas = 0, n = 0
      for (let d = ini; d <= fin; d++) {
        const r = horasMapa.value[fechaDe(gAnio.value, gMes.value, d)]
        if (r) { horas += r.horas; n += r.n }
      }
      out.push({ id: `s${s}`, etiqueta: `Sem ${s}`, sub: `${ini}–${fin}`, horas, n, titulo: `Semana ${s} (${ini}–${fin} ${MESES_NOMBRE[gMes.value - 1]}): ${fmtNum(horas)} h · ${n} registro(s). Clic para ver los días.` })
    }
  } else {
    const { ini, fin } = rangoSemana(gAnio.value, gMes.value, gSem.value)
    for (let d = ini; d <= fin; d++) {
      const f = fechaDe(gAnio.value, gMes.value, d)
      const r = horasMapa.value[f] || { horas: 0, n: 0 }
      out.push({ id: f, etiqueta: String(d), sub: MESES_NOMBRE[gMes.value - 1].slice(0, 3), horas: r.horas, n: r.n, titulo: `${f}: ${fmtNum(r.horas)} h · ${r.n} registro(s). ${props.textoAccionDia}` })
    }
  }
  return out
})
const totalVista = computed(() => barrasHora.value.reduce((t, b) => t + b.horas, 0))
const promVista = computed(() => (barrasHora.value.length ? totalVista.value / barrasHora.value.length : 0))
// Escala: días siempre 0–24; agregados con máximo "bonito".
function techoBonito(v) {
  if (v <= 0) return 24
  const pot = Math.pow(10, Math.floor(Math.log10(v)))
  for (const m of [1, 2, 2.5, 5, 10]) if (m * pot >= v) return m * pot
  return 10 * pot
}
const escalaMax = computed(() => (vistaHora.value === 'semana' ? 24 : techoBonito(Math.max(...barrasHora.value.map((b) => b.horas), 0))))
const escalaTicks = computed(() => {
  if (vistaHora.value === 'semana') return [0, 6, 12, 18, 24]
  const max = escalaMax.value
  return [0, 1, 2, 3, 4].map((i) => Math.round((max * i) / 4 * 100) / 100)
})
function alturaHora(h) { return `${Math.max(0, Math.min(100, (Number(h) / (escalaMax.value || 1)) * 100))}%` }
const tituloVista = computed(() => (
  vistaHora.value === 'anual' ? `Año ${gAnio.value}`
  : vistaHora.value === 'mes' ? `${MESES_NOMBRE[gMes.value - 1]} ${gAnio.value}`
  : `Semana ${gSem.value} · ${MESES_NOMBRE[gMes.value - 1]} ${gAnio.value}`
))
// Navegación
const aniosHoraOptions = computed(() => {
  const actual = Number(hoyColombia().slice(0, 4))
  const out = []
  for (let y = actual; y >= actual - 4; y--) out.push({ value: y, label: String(y) })
  return out
})
const mesesHoraOptions = computed(() => MESES_NOMBRE.map((n, i) => ({ value: i + 1, label: n })))
function clicBarra(b) {
  if (vistaHora.value === 'anual') { gMes.value = Number(b.id.slice(1)); vistaHora.value = 'mes' }
  else if (vistaHora.value === 'mes') { gSem.value = Number(b.id.slice(1)); vistaHora.value = 'semana' }
  else emit('click-dia', b.id)
}
function irVista(v) { vistaHora.value = v }
async function pasoHora(dir) {
  if (vistaHora.value === 'anual') { gAnio.value += dir; await cargarAnio() }
  else if (vistaHora.value === 'mes') {
    gMes.value += dir
    if (gMes.value < 1) { gMes.value = 12; gAnio.value -= 1; await cargarAnio() }
    else if (gMes.value > 12) { gMes.value = 1; gAnio.value += 1; await cargarAnio() }
  } else {
    gSem.value += dir
    if (gSem.value < 1) {
      if (gMes.value === 1) { gMes.value = 12; gAnio.value -= 1; await cargarAnio() } else gMes.value -= 1
      gSem.value = 4
    } else if (gSem.value > 4) {
      if (gMes.value === 12) { gMes.value = 1; gAnio.value += 1; await cargarAnio() } else gMes.value += 1
      gSem.value = 1
    }
  }
}

onMounted(() => { if (anioCargado.value !== gAnio.value) cargarAnio() })
defineExpose({ recargar })
</script>

<template>
  <div class="chart-wrap">
    <div class="chart-head">
      <div>
        <strong>Horas de servicio — {{ tituloVista }}</strong>
        <div class="crumbs">
          <button :class="{ active: vistaHora === 'anual' }" @click="irVista('anual')">{{ gAnio }}</button>
          <span>›</span>
          <button :class="{ active: vistaHora === 'mes' }" :disabled="vistaHora === 'anual'" @click="irVista('mes')">{{ MESES_NOMBRE[gMes - 1] }}</button>
          <span v-if="vistaHora === 'semana'">›</span>
          <button v-if="vistaHora === 'semana'" class="active">Sem {{ gSem }}</button>
        </div>
      </div>
      <div class="chart-tools">
        <div class="seg">
          <button :class="{ active: vistaHora === 'anual' }" @click="irVista('anual')">Año</button>
          <button :class="{ active: vistaHora === 'mes' }" @click="irVista('mes')">Mes</button>
          <button :class="{ active: vistaHora === 'semana' }" @click="irVista('semana')">Semana</button>
        </div>
        <div class="field" style="min-width:110px;margin:0">
          <SearchableSelect v-model="gAnio" :options="aniosHoraOptions" placeholder="Año" @update:model-value="cargarAnio" />
        </div>
        <div class="field" v-if="vistaHora !== 'anual'" style="min-width:130px;margin:0">
          <SearchableSelect v-model="gMes" :options="mesesHoraOptions" placeholder="Mes" />
        </div>
        <button class="btn btn-ghost btn-sm" @click="pasoHora(-1)" title="Anterior"><AppIcon name="chevronLeft" :size="16" /></button>
        <button class="btn btn-ghost btn-sm" @click="pasoHora(1)" title="Siguiente"><AppIcon name="chevronRight" :size="16" /></button>
      </div>
    </div>
    <p class="muted chart-sub">Total: <strong>{{ fmtNum(totalVista) }} h</strong> · Promedio: <strong>{{ fmtNum(promVista) }} h</strong> · Escala 0–{{ fmtNum(escalaMax) }} h · Clic en una barra para {{ vistaHora === 'anual' ? 'ver sus semanas' : vistaHora === 'mes' ? 'ver sus días' : textoAccionDia.toLowerCase() }}</p>
    <div v-if="graficoCargando" class="chart-skeleton" role="status" aria-live="polite" aria-label="Cargando gráfico">
      <p class="skeleton-status"><span class="spinner" aria-hidden="true"></span>Cargando gráfico…</p>
      <div class="chart-skeleton-bars" aria-hidden="true">
        <div v-for="n in 8" :key="'hsk' + n" class="skeleton-line" :style="{ height: `${18 + (n % 4) * 18}%` }"></div>
      </div>
    </div>
    <div v-else-if="!barrasHora.length" class="muted">Sin datos para graficar.</div>
    <div v-else class="chart-plot">
      <div class="chart-y">
        <span v-for="t in [...escalaTicks].reverse()" :key="t">{{ fmtNum(t) }}</span>
      </div>
      <div class="chart-area">
        <div class="chart-grid">
          <div v-for="t in escalaTicks" :key="t" class="chart-gridline"></div>
          <div
            v-if="promVista > 0"
            class="chart-avg"
            :style="{ bottom: `${Math.max(0, Math.min(100, (promVista / escalaMax) * 100))}%` }"
          ><span class="chart-avg-label">⌀ {{ fmtNum(promVista) }}</span></div>
        </div>
        <div class="chart-bars">
          <div v-for="b in barrasHora" :key="b.id" class="chart-col" :title="b.titulo" @click="clicBarra(b)">
            <span class="chart-val">{{ fmtNum(b.horas) }}</span>
            <div class="chart-track"><div class="chart-bar" :style="{ height: alturaHora(b.horas) }"></div></div>
            <span class="chart-label">{{ b.etiqueta }}</span>
            <span class="chart-sub2">{{ b.sub }}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="chart-legend">
      <span class="lg"><i class="sw sw-bar"></i>Horas de servicio</span>
      <span class="lg"><i class="sw sw-avg"></i>Promedio ({{ fmtNum(promVista) }} h)</span>
      <span class="lg muted">Eje 0–{{ fmtNum(escalaMax) }} h</span>
    </div>
  </div>
</template>

<style scoped>
/* Skeleton de carga del gráfico */
.chart-skeleton { padding: .8rem 0; }
.skeleton-status { display: flex; align-items: center; gap: .6rem; color: var(--acr-azul); font-size: .85rem; margin: 0 0 .6rem; }
.skeleton-status .spinner { width: 18px; height: 18px; margin: 0; border-width: 2px; }
.chart-skeleton-bars { display: flex; align-items: flex-end; gap: .5rem; height: 210px; border-bottom: 2px solid var(--acr-borde); padding: 0 .4rem; }
.chart-skeleton-bars .skeleton-line { flex: 1; min-width: 44px; border-radius: 7px 7px 0 0; background: var(--acr-gris, #EAF1FB); animation: skeleton-pulse 1.4s ease-in-out infinite; }
@keyframes skeleton-pulse { 50% { opacity: .4; } }
@media (prefers-reduced-motion: reduce) {
  .chart-skeleton-bars .skeleton-line, .skeleton-status .spinner { animation: none; }
}

/* Gráfico de horas de servicio: parece un gráfico real (ejes, fondo, leyenda) */
.chart-wrap {
  background: linear-gradient(180deg, var(--acr-azul-50) 0%, #fff 30%);
  border: 1px solid var(--acr-borde); border-radius: 12px;
  padding: 1rem 1.1rem; margin-bottom: 1rem; box-shadow: var(--acr-sombra-sm);
}
.chart-head { display: flex; justify-content: space-between; align-items: flex-start; gap: .8rem; flex-wrap: wrap; margin-bottom: .3rem; }
.chart-tools { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; }
.crumbs { display: flex; align-items: center; gap: .3rem; margin-top: .2rem; font-size: .8rem; color: var(--acr-texto-suave); }
.crumbs button { border: none; background: none; cursor: pointer; font: inherit; color: var(--acr-azul); font-weight: 600; padding: .1rem .3rem; border-radius: 6px; }
.crumbs button:hover:not(:disabled) { background: var(--acr-azul-50); }
.crumbs button.active { background: var(--acr-azul); color: #fff; }
.crumbs button:disabled { cursor: default; color: var(--acr-texto-suave); }
.seg { display: inline-flex; border: 1px solid var(--acr-borde); border-radius: 999px; overflow: hidden; background: #fff; }
.seg button { border: none; background: #fff; padding: .3rem .7rem; font-size: .78rem; font-weight: 700; cursor: pointer; color: var(--acr-texto-suave); font-family: inherit; }
.seg button.active { background: var(--acr-azul); color: #fff; }
.chart-sub { font-size: .8rem; margin: 0 0 .6rem; }
.chart-plot { display: flex; gap: .5rem; }
.chart-y { display: flex; flex-direction: column; justify-content: space-between; font-size: .7rem; color: var(--acr-texto-suave); text-align: right; padding: .8rem 0 2.6rem; font-variant-numeric: tabular-nums; }
.chart-area { position: relative; flex: 1; background: #fff; border: 1px solid var(--acr-borde); border-radius: 10px; padding: .8rem .8rem 0; min-width: 0; }
.chart-grid { position: absolute; inset: .8rem .8rem 2.6rem; display: flex; flex-direction: column; justify-content: space-between; pointer-events: none; }
.chart-gridline { border-top: 1px dashed #D8E4F3; }
.chart-gridline:last-child { border-top-style: solid; border-color: var(--acr-borde); }
.chart-avg { position: absolute; left: 0; right: 0; height: 0; border-top: 2px dashed var(--acr-bad); z-index: 2; pointer-events: none; }
.chart-avg-label { position: absolute; right: 0; top: -1.3rem; background: var(--acr-bad-bg); color: var(--acr-bad); font-size: .68rem; font-weight: 700; padding: .05rem .45rem; border-radius: 999px; border: 1px solid #f1c2c2; white-space: nowrap; }
.chart-bars { position: relative; display: flex; align-items: stretch; gap: .4rem; min-height: 210px; overflow-x: auto; padding-bottom: 0; }
.chart-col { flex: 1; min-width: 44px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 2px; cursor: pointer; border-radius: 8px; padding: .15rem .1rem 0; }
.chart-col:hover { background: var(--acr-azul-50); }
.chart-col:hover .chart-bar { filter: brightness(1.12); }
.chart-val { font-size: .7rem; font-weight: 800; color: var(--acr-azul-700); font-variant-numeric: tabular-nums; }
.chart-track { width: 100%; max-width: 52px; height: 150px; background: #EDF2F9; border: 1px solid var(--acr-borde); border-radius: 8px 8px 4px 4px; display: flex; align-items: flex-end; overflow: hidden; }
.chart-bar { width: 100%; background: linear-gradient(180deg, #3A7BD0 0%, var(--acr-azul) 100%); border-radius: 7px 7px 0 0; min-height: 3px; transition: height .25s; }
.chart-label { font-size: .7rem; font-weight: 700; white-space: nowrap; }
.chart-sub2 { font-size: .66rem; color: var(--acr-texto-suave); white-space: nowrap; margin-bottom: .4rem; font-variant-numeric: tabular-nums; }
.chart-legend { display: flex; gap: 1rem; flex-wrap: wrap; margin-top: .6rem; font-size: .78rem; color: var(--acr-texto-suave); align-items: center; }
.chart-legend .lg { display: inline-flex; align-items: center; gap: .35rem; }
.chart-legend .sw { width: 14px; height: 10px; border-radius: 3px; display: inline-block; }
.sw-bar { background: var(--acr-azul); }
.sw-avg { height: 0 !important; width: 18px !important; border-top: 2px dashed var(--acr-bad); border-radius: 0 !important; }
</style>
