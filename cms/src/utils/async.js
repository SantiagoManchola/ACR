// Estados de carga reutilizables para botones asíncronos.
// Un botón que llama a un servicio debe deshabilitarse y mostrar
// "cargando" hasta que la petición termine (o falle).
import { ref } from 'vue'

export function useBusy() {
  const busy = ref(false)
  async function run(fn) {
    if (busy.value) return
    busy.value = true
    try {
      return await fn()
    } finally {
      busy.value = false
    }
  }
  return { busy, run }
}
