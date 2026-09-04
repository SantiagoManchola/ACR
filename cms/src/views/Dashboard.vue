<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useInventarioStore } from '../stores/inventario'
import { useMicromedidoresStore } from '../stores/micromedidores'
import { usePlantaStore } from '../stores/planta'
import AppIcon from '../components/AppIcon.vue'

const auth = useAuthStore()
const router = useRouter()
const inv = useInventarioStore()
const mm = useMicromedidoresStore()
const planta = usePlantaStore()

const kpis = ref([])
const rol = computed(() => auth.rol)

async function load() {
  const tareas = []
  if (['admin', 'administrativo'].includes(rol.value)) {
    tareas.push(inv.loadElementos(), inv.loadAlertas(), mm.loadSuscriptores(), mm.loadMicromedidores())
  }
  if (['admin', 'operario'].includes(rol.value)) {
    tareas.push(planta.loadFueraRango())
  }
  await Promise.allSettled(tareas)
  buildKpis()
}

function buildKpis() {
  const out = []
  if (['admin', 'administrativo'].includes(rol.value)) {
    out.push({ label: 'Elementos en inventario', value: inv.elementos.length, to: '/inventario', icon: 'inventory' })
    out.push({ label: 'Alertas de existencia', value: inv.alertas.length, to: '/inventario', icon: 'alert', tone: inv.alertas.length ? 'bad' : 'ok' })
    out.push({ label: 'Suscriptores', value: mm.suscriptores.length, to: '/micromedidores', icon: 'users' })
    out.push({ label: 'Micromedidores', value: mm.micromedidores.length, to: '/micromedidores', icon: 'gauge' })
  }
  if (['admin', 'operario'].includes(rol.value)) {
    out.push({ label: 'Parámetros fuera de rango', value: planta.fueraRango.length, to: '/planta', icon: 'alert', tone: planta.fueraRango.length ? 'warn' : 'ok' })
  }
  kpis.value = out
}

const enlaces = computed(() => {
  const map = {
    admin: [['inventario', 'Inventario', 'inventory'], ['micromedidores', 'Micromedidores', 'gauge'], ['planta', 'Planta', 'drop'], ['reportes', 'Reportes', 'report'], ['usuarios', 'Usuarios', 'users']],
    administrativo: [['inventario', 'Inventario', 'inventory'], ['micromedidores', 'Micromedidores', 'gauge'], ['reportes', 'Reportes', 'report']],
    operario: [['planta', 'Planta', 'drop'], ['reportes', 'Reportes', 'report']],
    fontanero: [['micromedidores', 'Lecturas', 'gauge']],
  }
  return map[rol.value] || []
})

onMounted(load)
</script>

<template>
  <div>
    <h1>Bienvenido, {{ auth.nombre || 'usuario' }}</h1>
    <p class="muted">Rol: <span style="text-transform:capitalize;font-weight:600">{{ rol }}</span> · Acueducto Comunitario Acuaricaurte — Ibagué, Tolima</p>

    <div class="kpi-grid mt-2">
      <div class="kpi" v-for="k in kpis" :key="k.label" @click="router.push(k.to)" style="cursor:pointer">
        <div class="flex center gap-1">
          <AppIcon :name="k.icon" :size="16" />
          <span class="label">{{ k.label }}</span>
        </div>
        <div class="value" :class="k.tone === 'bad' ? 'bad' : k.tone === 'warn' ? 'warn' : ''">{{ k.value }}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-head">
        <div class="title"><AppIcon name="dashboard" /><h3>Accesos rápidos</h3></div>
      </div>
      <div class="flex wrap gap-1">
        <button v-for="[to, label, icon] in enlaces" :key="to" class="btn btn-ghost" @click="router.push('/' + to)">
          <AppIcon :name="icon" /> {{ label }}
        </button>
      </div>
    </div>
  </div>
</template>
