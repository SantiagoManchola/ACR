<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppIcon from '../components/AppIcon.vue'
import PasswordInput from '../components/PasswordInput.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')

async function submit() {
  const ok = await auth.login(username.value.trim(), password.value)
  if (ok) router.push('/dashboard')
}
</script>

<template>
  <div class="login-page">
    <aside class="login-hero">
      <span class="logo-big"><AppIcon name="drop" :size="34" /></span>
      <h1>Acueducto Comunitario Acuaricaurte</h1>
      <p>Panel operativo de gestión: inventario, micromedidores, planta de tratamiento y reportes, en un solo lugar.</p>
      <ul>
        <li>Registro de inventario y movimientos</li>
        <li>Gestión de micromedidores y lecturas</li>
        <li>Control de la planta de tratamiento</li>
        <li>Reportes exportables (CSV · Excel · PDF)</li>
      </ul>
    </aside>

    <section class="login-form-side">
      <div class="login-card card">
        <div class="brand-mini"><AppIcon name="drop" :size="22" /><span>ACR</span></div>
        <h2 style="text-align:center;margin-bottom:1.2rem">Iniciar sesión</h2>

        <form @submit.prevent="submit">
          <div class="field">
            <label for="u">Usuario</label>
            <input id="u" class="input" v-model="username" autocomplete="username" placeholder="su usuario" required />
          </div>
          <div class="field">
            <label for="p">Contraseña</label>
            <PasswordInput id="p" v-model="password" placeholder="••••••" required autocomplete="current-password" />
          </div>

          <BaseAlert v-if="auth.error" type="bad" class="mb-1">{{ auth.error }}</BaseAlert>

          <button class="btn btn-primary btn-block" type="submit" :disabled="auth.loading">
            <span v-if="auth.loading">Cargando…</span>
            <span v-else>Entrar</span>
          </button>
        </form>
        <p class="muted" style="text-align:center;font-size:.78rem;margin-top:1rem">
          Ibagué · Tolima · Colombia
        </p>
      </div>
    </section>
  </div>
</template>

<script>
import BaseAlert from '../components/BaseAlert.vue'
export default { components: { BaseAlert } }
</script>
