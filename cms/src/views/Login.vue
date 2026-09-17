<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppIcon from '../components/AppIcon.vue'
import PasswordInput from '../components/PasswordInput.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const sesionExpirada = computed(() => route.query.sesion === 'expirada')

async function submit() {
  const ok = await auth.login(username.value.trim(), password.value)
  if (ok) router.push('/dashboard')
}
</script>

<template>
  <div class="login-page">
    <aside class="login-hero">
      <div class="login-hero-inner">
        <span class="logo-big"><img src="/acr-logo.png" alt="ACR" /></span>
        <h1>Acueducto Comunitario Acuaricaurte</h1>
        <span class="hero-div"></span>
        <p class="hero-loc">Ibagué · Tolima · Colombia</p>
      </div>
      <p class="hero-note"><AppIcon name="lock" :size="13" /> Acceso institucional</p>
    </aside>

    <section class="login-form-side">
      <div class="login-card card">
        <div class="brand-mini"><img src="/acr-logo.png" alt="ACR" /><span>ACR</span></div>
        <h2>Bienvenido</h2>
        <p class="login-sub">Ingresa tus credenciales para continuar</p>

        <form @submit.prevent="submit">
          <div class="field">
            <label for="u">Usuario</label>
            <div class="input-wrap">
              <AppIcon name="user" :size="18" />
              <input id="u" class="input" v-model="username" autocomplete="username" placeholder="su usuario" required />
            </div>
          </div>
          <div class="field">
            <label for="p">Contraseña</label>
            <PasswordInput id="p" v-model="password" icon="lock" placeholder="••••••" required autocomplete="current-password" />
          </div>

          <BaseAlert v-if="sesionExpirada" type="info" class="mb-1">Tu sesión expiró por seguridad. Ingresa de nuevo para continuar.</BaseAlert>
          <BaseAlert v-if="auth.error" type="bad" class="mb-1">{{ auth.error }}</BaseAlert>

          <button class="btn btn-primary btn-block" type="submit" :disabled="auth.loading">
            <span v-if="auth.loading">Cargando…</span>
            <span v-else>Entrar</span>
          </button>
        </form>
        <p class="login-foot">© Acueducto Comunitario Acuaricaurte</p>
      </div>
    </section>
  </div>
</template>

<script>
import BaseAlert from '../components/BaseAlert.vue'
export default { components: { BaseAlert } }
</script>
