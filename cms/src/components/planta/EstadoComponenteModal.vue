<script setup>
import { computed, ref, watch } from 'vue'
import BaseModal from '../BaseModal.vue'
import BaseAlert from '../BaseAlert.vue'
import AppIcon from '../AppIcon.vue'
import { ESTADOS_PLANTA_OPTIONS, estadoPlantaMeta } from '../../utils/estadoPlanta'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  componente: { type: Object, default: null },
  saving: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue', 'save', 'clear-error'])

const estado = ref('funcionando')
const nota = ref('')
const localError = ref('')

const metaActual = computed(() => estadoPlantaMeta(props.componente?.estado_actual))
const notaObligatoria = computed(() => estado.value !== 'funcionando')
const errorMostrado = computed(() => localError.value || props.error)

watch(
  () => [props.modelValue, props.componente?.id],
  () => {
    if (!props.modelValue || !props.componente) return
    estado.value = props.componente.estado_actual || 'funcionando'
    nota.value = ''
    localError.value = ''
  },
  { immediate: true },
)
watch(estado, () => { localError.value = ''; emit('clear-error') })
watch(nota, () => { if (localError.value) localError.value = ''; emit('clear-error') })

function cerrar() {
  emit('update:modelValue', false)
}

function guardar() {
  localError.value = ''
  if (notaObligatoria.value && !nota.value.trim()) {
    localError.value = 'La nota es obligatoria para Afectación o Fuera de funcionamiento.'
    return
  }
  emit('save', {
    estado: estado.value,
    nota: nota.value.trim() || null,
  })
}
</script>

<template>
  <BaseModal
    :model-value="modelValue"
    :title="componente ? `Actualizar estado · ${componente.nombre}` : 'Actualizar estado'"
    size="620"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <template v-if="componente">
      <div class="estado-actual-card" :class="`estado-${metaActual.color}`">
        <div>
          <span class="muted">Estado actual</span>
          <strong>{{ metaActual.label }}</strong>
        </div>
        <div v-if="componente.nota_actual" class="estado-actual-nota">
          {{ componente.nota_actual }}
        </div>
        <div v-if="componente.fecha_actualizacion" class="estado-actual-fecha">
          Última actualización: {{ componente.fecha_actualizacion }}
          <template v-if="componente.hora_actualizacion"> · {{ String(componente.hora_actualizacion).slice(0, 5) }}</template>
          <template v-if="componente.responsable_nombre"> · {{ componente.responsable_nombre }}</template>
        </div>
      </div>

      <BaseAlert v-if="errorMostrado" type="bad" class="mb-1">{{ errorMostrado }}</BaseAlert>

      <div class="field">
        <label>Nuevo estado *</label>
        <div class="opciones-estado" role="radiogroup" aria-label="Nuevo estado de la parte">
          <label
            v-for="opcion in ESTADOS_PLANTA_OPTIONS"
            :key="opcion.value"
            class="opcion-estado"
            :class="[`estado-${opcion.color}`, { activa: estado === opcion.value }]"
          >
            <input v-model="estado" type="radio" :value="opcion.value" name="estado-planta" />
            <span class="dot" aria-hidden="true"></span>
            <span class="opcion-texto">
              <strong>{{ opcion.label }}</strong>
              <small>{{ opcion.descripcion }}</small>
            </span>
            <AppIcon v-if="estado === opcion.value" name="check" :size="18" class="opcion-check" />
          </label>
        </div>
      </div>

      <div class="field">
        <label>Nota {{ notaObligatoria ? '*' : '(opcional)' }}</label>
        <textarea
          v-model="nota"
          class="textarea"
          rows="3"
          maxlength="2000"
          :placeholder="notaObligatoria ? 'Describe la afectación o el motivo por el que está fuera de funcionamiento…' : 'Observación opcional sobre el estado…'"
        ></textarea>
        <p class="hint" v-if="notaObligatoria">La nota es obligatoria porque la parte no está en funcionamiento normal.</p>
      </div>
    </template>

    <template #footer>
      <button class="btn btn-ghost" :disabled="saving" @click="cerrar">Cancelar</button>
      <button class="btn btn-primary" :disabled="saving || !componente" @click="guardar">
        <span v-if="saving" class="spinner"></span>{{ saving ? 'Guardando…' : 'Guardar estado' }}
      </button>
    </template>
  </BaseModal>
</template>

<style scoped>
.estado-actual-card {
  border: 1px solid var(--acr-borde);
  border-left: 4px solid currentColor;
  border-radius: var(--acr-radio-sm);
  padding: .7rem .8rem;
  margin-bottom: 1rem;
  background: #fff;
  display: flex;
  flex-direction: column;
  gap: .18rem;
  color: var(--acr-texto-suave);
}
.estado-actual-card strong { display: block; color: var(--acr-texto); font-size: 1rem; }
.estado-actual-card.estado-ok { border-left-color: var(--acr-ok); }
.estado-actual-card.estado-warn { border-left-color: var(--acr-warn); }
.estado-actual-card.estado-bad { border-left-color: var(--acr-bad); }
.estado-actual-card.estado-muted { border-left-color: var(--acr-texto-suave); }
.estado-actual-nota { color: var(--acr-texto); font-size: .86rem; }
.estado-actual-fecha { font-size: .74rem; }
.opciones-estado { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: .55rem; }
.opcion-estado {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: .55rem;
  border: 1px solid var(--acr-borde);
  border-top: 4px solid var(--acr-borde);
  border-radius: var(--acr-radio-sm);
  padding: .7rem .65rem;
  background: #fff;
  cursor: pointer;
  transition: background .15s, border-color .15s, box-shadow .15s;
}
.opcion-estado input { position: absolute; opacity: 0; pointer-events: none; }
.opcion-estado:focus-within { outline: 2px solid var(--acr-azul); outline-offset: 2px; }
.opcion-estado .dot { width: 10px; height: 10px; border-radius: 50%; background: currentColor; margin-top: .25rem; flex: none; }
.opcion-texto { display: flex; flex-direction: column; gap: .16rem; min-width: 0; }
.opcion-texto strong { color: var(--acr-texto); font-size: .84rem; line-height: 1.25; }
.opcion-texto small { color: var(--acr-texto-suave); font-size: .72rem; line-height: 1.3; }
.opcion-check { margin-left: auto; color: currentColor; flex: none; }
.opcion-estado.estado-ok { color: var(--acr-ok); border-top-color: var(--acr-ok); }
.opcion-estado.estado-warn { color: var(--acr-warn); border-top-color: var(--acr-warn); }
.opcion-estado.estado-bad { color: var(--acr-bad); border-top-color: var(--acr-bad); }
.opcion-estado.activa { background: var(--acr-azul-50); box-shadow: 0 0 0 2px var(--acr-azul); }
.opcion-estado.estado-ok.activa { background: var(--acr-ok-bg); box-shadow: 0 0 0 2px var(--acr-ok); }
.opcion-estado.estado-warn.activa { background: var(--acr-warn-bg); box-shadow: 0 0 0 2px var(--acr-warn); }
.opcion-estado.estado-bad.activa { background: var(--acr-bad-bg); box-shadow: 0 0 0 2px var(--acr-bad); }
@media (max-width: 700px) {
  /* En móvil las tres opciones van una debajo de otra, con altura y aire */
  .opciones-estado { grid-template-columns: 1fr; gap: .65rem; }
  .opcion-estado {
    align-items: center;
    min-height: 64px;
    padding: .8rem .75rem;
    gap: .65rem;
  }
  .opcion-estado .dot { width: 12px; height: 12px; margin-top: 0; }
  .opcion-texto { gap: .2rem; }
  .opcion-texto strong { font-size: .9rem; }
  .opcion-texto small { font-size: .76rem; line-height: 1.35; }
  .opcion-check { width: 20px; height: 20px; }
  .estado-actual-card { padding: .8rem .9rem; gap: .25rem; }
}
</style>
