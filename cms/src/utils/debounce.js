// Debounce simple para búsquedas/filtros automáticos.
// Uso: const f = debounce(() => cargar(), 350); f(); f.cancel()
export function debounce(fn, wait = 350) {
  let timer = null
  const wrapped = (...args) => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => { timer = null; fn(...args) }, wait)
  }
  wrapped.cancel = () => { if (timer) clearTimeout(timer); timer = null }
  return wrapped
}
