<script setup>
import { ref } from 'vue'
import AppIcon from './AppIcon.vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  label: { type: String, default: '' },
  required: { type: Boolean, default: false },
  placeholder: { type: String, default: '' },
  autocomplete: { type: String, default: 'new-password' },
  id: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const show = ref(false)
</script>

<template>
  <div class="field" style="margin-bottom:.85rem">
    <label v-if="label">{{ label }}<span v-if="required" style="color:var(--acr-bad)"> *</span></label>
    <div style="position:relative">
      <input
        class="input"
        :id="id"
        :type="show ? 'text' : 'password'"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :autocomplete="autocomplete"
        @input="emit('update:modelValue', $event.target.value)"
      />
      <button
        type="button"
        class="pw-toggle"
        @click="show = !show"
        :aria-label="show ? 'Ocultar contraseña' : 'Mostrar contraseña'"
      >
        <AppIcon :name="show ? 'eyeOff' : 'eye'" :size="18" />
      </button>
    </div>
  </div>
</template>

<style scoped>
.pw-toggle {
  position: absolute; right: 6px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--acr-texto-suave);
  display: grid; place-items: center; padding: 4px; border-radius: 6px;
}
.pw-toggle:hover { color: var(--acr-azul); background: var(--acr-azul-50); }
</style>
