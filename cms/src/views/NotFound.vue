<script setup>
import { useRouter } from 'vue-router'
import AppIcon from '../components/AppIcon.vue'
const router = useRouter()
</script>

<template>
  <div class="state-block" style="padding-top:4rem">
    <AppIcon name="alert" :size="40" />
    <h2 style="margin-top:1rem">Página no encontrada</h2>
    <p>La ruta solicitada no existe en el panel ACR.</p>
    <button class="btn btn-primary mt-1" @click="router.push('/dashboard')"><AppIcon name="home" />Ir al inicio</button>
  </div>
</template>
