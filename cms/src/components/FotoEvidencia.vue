<script setup>
import { computed, ref, watch } from 'vue'
import AppIcon from './AppIcon.vue'
import { apiError } from '../api/http'
import { subirEvidencia } from '../api/evidencias'

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

/* Reactivo para que los formularios puedan deshabilitar su botón de guardar
   mientras la imagen se está subiendo (cualquier componente que lo use). */
const subiendo = computed(() => estado.value === 'subiendo')

watch(() => props.modelValue, (v) => {
  vistaPrevia.value = v || ''
  if (!v) { estado.value = 'idle'; mensaje.value = '' }
  else if (estado.value !== 'subiendo') { estado.value = 'listo' }
})

function elegir() {
  if (props.disabled || subiendo.value) return
  inputRef.value?.click()
}

async function alElegir(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file) return
  estado.value = 'subiendo'
  mensaje.value = 'Preparando foto…'
  try {
    const { public_url } = await subirEvidencia(props.modulo, file, (paso) => { mensaje.value = paso })
    vistaPrevia.value = public_url
    emit('update:modelValue', public_url)
    estado.value = 'listo'
    mensaje.value = 'Foto lista'
  } catch (err) {
    estado.value = 'error'
    mensaje.value = apiError(err, 'No se pudo subir la foto.')
  }
}

function quitar() {
  if (subiendo.value) return
  vistaPrevia.value = ''
  emit('update:modelValue', '')
  estado.value = 'idle'
  mensaje.value = ''
}

defineExpose({ ocupado: () => subiendo.value, subiendo })
</script>

<template>
  <div class="field foto-campo" :class="{ 'foto-ocupado': subiendo }">
    <label>{{ label }}</label>
    <input ref="inputRef" type="file" accept="image/*" capture="environment" style="display:none" @change="alElegir" />

    <!-- Sin foto aún: zona para tomar/seleccionar (con loader mientras sube) -->
    <div v-if="!vistaPrevia" class="foto-drop" :class="{ 'foto-drop-subiendo': subiendo }" @click="elegir">
      <template v-if="subiendo">
        <span class="foto-spinner" aria-hidden="true"></span>
        <span class="foto-paso">Subiendo foto…</span>
        <small class="muted">{{ mensaje || 'Preparando imagen…' }}</small>
        <div class="foto-progreso" aria-hidden="true"><div class="foto-progreso-barra"></div></div>
        <small class="muted">Espera a que termine: el botón de guardar está deshabilitado.</small>
      </template>
      <template v-else>
        <AppIcon name="camera" :size="22" />
        <span>Tomar o seleccionar foto</span>
      </template>
    </div>

    <!-- Con foto: vista previa con overlay de subida al cambiarla -->
    <div v-else class="foto-prev">
      <div class="foto-prev-img">
        <img :src="vistaPrevia" alt="Evidencia" />
        <div v-if="subiendo" class="foto-overlay">
          <span class="foto-spinner" aria-hidden="true"></span>
          <span class="foto-paso">Subiendo foto…</span>
          <small>{{ mensaje }}</small>
        </div>
      </div>
      <div class="foto-acciones">
        <button class="btn btn-ghost btn-sm" @click="elegir" :disabled="disabled || subiendo">Cambiar</button>
        <button class="btn btn-ghost btn-sm" @click="quitar" :disabled="disabled || subiendo">Quitar</button>
        <span v-if="subiendo" class="foto-paso muted">{{ mensaje }}</span>
      </div>
    </div>

    <p v-if="mensaje && !subiendo" class="hint" :class="{ 'foto-err': estado === 'error' }">{{ mensaje }}</p>
  </div>
</template>

<style scoped>
.foto-campo { position: relative; }
.foto-drop {
  border: 1.5px dashed var(--acr-borde); border-radius: var(--acr-radio-sm);
  background: #FBFDFF; padding: 1rem; text-align: center; cursor: pointer;
  display: flex; flex-direction: column; align-items: center; gap: .35rem;
  color: var(--acr-azul-700); font-weight: 600; font-size: .88rem;
}
.foto-drop:hover { background: var(--acr-azul-50); }
.foto-drop-subiendo { cursor: progress; background: var(--acr-azul-50); }
.foto-prev { display: flex; gap: .7rem; align-items: flex-start; }
.foto-prev-img { position: relative; flex: none; }
.foto-prev img { width: 120px; height: 90px; object-fit: cover; border-radius: 8px; border: 1px solid var(--acr-borde); display: block; }
.foto-acciones { display: flex; flex-direction: column; gap: .4rem; }
.foto-err { color: var(--acr-bad); }

/* Loader claro de subida */
.foto-spinner {
  width: 26px; height: 26px; border: 3px solid var(--acr-azul-50);
  border-top-color: var(--acr-azul); border-radius: 50%;
  animation: spin .7s linear infinite; display: inline-block; flex: none;
}
.foto-paso { font-weight: 700; }

.foto-progreso {
  width: min(320px, 90%); height: 6px; border-radius: 999px;
  background: var(--acr-azul-50); overflow: hidden; margin-top: .15rem;
}
.foto-progreso-barra {
  width: 40%; height: 100%; border-radius: 999px; background: var(--acr-azul);
  animation: foto-slide 1.1s ease-in-out infinite;
}
@keyframes foto-slide {
  0% { transform: translateX(-110%); }
  100% { transform: translateX(260%); }
}

.foto-overlay {
  position: absolute; inset: 0; border-radius: 8px;
  background: rgba(15, 42, 74, .62); color: #fff;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: .3rem; text-align: center; padding: .4rem; font-size: .78rem;
}
.foto-overlay .foto-spinner { border-color: rgba(255, 255, 255, .35); border-top-color: #fff; }
.foto-overlay .foto-paso { font-size: .82rem; }
</style>
