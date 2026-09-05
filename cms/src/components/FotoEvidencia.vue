<script setup>
import { ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'
import { apiError } from '../api/http'
import { subirEvidencia } from '../api/evidencias'
import { formatoKB } from '../utils/imagen'

const props = defineProps({
  modelValue: { type: String, default: '' }, // URL pública en R2 (o '')
  modulo: { type: String, required: true }, // medicion | lectura | actividad
  label: { type: String, default: 'Foto de evidencia (opcional)' },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const inputRef = ref(null)
const vistaPrevia = ref(props.modelValue || '')
const estado = ref('idle') // idle | subiendo | listo | error
const mensaje = ref('')

watch(() => props.modelValue, (v) => {
  vistaPrevia.value = v || ''
  if (!v) { estado.value = 'idle'; mensaje.value = '' }
  else if (estado.value !== 'subiendo') { estado.value = 'listo' }
})

function elegir() { inputRef.value?.click() }

async function alElegir(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  estado.value = 'subiendo'
  mensaje.value = 'Comprimiendo imagen…'
  try {
    const { public_url, stats } = await subirEvidencia(props.modulo, file, (paso) => { mensaje.value = paso })
    vistaPrevia.value = public_url
    emit('update:modelValue', public_url)
    estado.value = 'listo'
    const ahorro = stats.antes > 0 ? Math.round((1 - stats.despues / stats.antes) * 100) : 0
    mensaje.value = `${formatoKB(stats.antes)} → ${formatoKB(stats.despues)} (ahorro ${ahorro}%)`
  } catch (err) {
    estado.value = 'error'
    mensaje.value = apiError(err, 'No se pudo subir la foto.')
  }
}

function quitar() {
  vistaPrevia.value = ''
  emit('update:modelValue', '')
  estado.value = 'idle'
  mensaje.value = ''
}

defineExpose({ ocupado: () => estado.value === 'subiendo' })
</script>

<template>
  <div class="field">
    <label>{{ label }}</label>
    <input ref="inputRef" type="file" accept="image/*" capture="environment" style="display:none" @change="alElegir" />
    <div v-if="!vistaPrevia" class="foto-drop" @click="!disabled && estado !== 'subiendo' && elegir()">
      <AppIcon name="camera" :size="22" />
      <span v-if="estado === 'subiendo'">Subiendo foto…</span>
      <span v-else>Tomar o seleccionar foto</span>
      <small class="muted">Se comprime sola antes de subirse (ahorra ~90% sin perder calidad)</small>
    </div>
    <div v-else class="foto-prev">
      <img :src="vistaPrevia" alt="Evidencia" />
      <div class="foto-acciones">
        <button class="btn btn-ghost btn-sm" @click="elegir" :disabled="disabled || estado === 'subiendo'">Cambiar</button>
        <button class="btn btn-ghost btn-sm" @click="quitar" :disabled="disabled || estado === 'subiendo'">Quitar</button>
      </div>
    </div>
    <p v-if="mensaje" class="hint" :class="{ 'foto-err': estado === 'error' }">{{ mensaje }}</p>
    <p v-else class="hint">Opcional. Si R2 no está configurado, puede guardar el registro sin foto.</p>
  </div>
</template>

<style scoped>
.foto-drop {
  border: 1.5px dashed var(--acr-borde); border-radius: var(--acr-radio-sm);
  background: #FBFDFF; padding: 1rem; text-align: center; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: .35rem;
  color: var(--acr-azul-700); font-weight: 600; font-size: .88rem;
}
.foto-drop:hover { background: var(--acr-azul-50); }
.foto-prev { display: flex; gap: .7rem; align-items: flex-start; }
.foto-prev img { width: 120px; height: 90px; object-fit: cover; border-radius: 8px; border: 1px solid var(--acr-borde); }
.foto-acciones { display: flex; flex-direction: column; gap: .4rem; }
.foto-err { color: var(--acr-bad); }
</style>
