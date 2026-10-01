// Compresión de imágenes en el navegador antes de subir a R2.
//
// Estrategia para no ocupar espacio de más sin perder calidad visible:
// - Redimensiona a un máximo de 1600px por el lado largo (suficiente para
//   evidencias en pantalla e impresión; una foto de 4000px no aporta más).
// - Convierte a WebP calidad 0.82 (~30-50% más liviano que JPEG a igual
//   calidad percibida). Si el navegador no soporta WebP, usa JPEG 0.85.
// - Resultado típico: foto de 3-5 MB -> 150-500 KB (ahorro ~90%).
export const MAX_DIMENSION = 1600
export const CALIDAD_WEBP = 0.82
export const CALIDAD_JPEG = 0.85
export const MAX_ENTRADA_BYTES = 20 * 1024 * 1024 // 20 MB (cámara moderna)

export function validarImagen(file) {
  if (!file) return 'Seleccione una imagen.'
  if (!file.type || !file.type.startsWith('image/')) return 'El archivo debe ser una imagen.'
  if (file.size > MAX_ENTRADA_BYTES) return 'La imagen supera los 20 MB.'
  return ''
}

/* Extrae la imagen del portapapeles en un evento paste (Ctrl/Cmd+V).
   Devuelve el Blob de la imagen o null si el portapapeles no trae imagen
   (p. ej. hay texto copiado); así el componente ignora el pegado de texto. */
export function imagenDesdePortapapeles(e) {
  const items = e.clipboardData?.items
  if (!items) return null
  for (const item of items) {
    if (item.type && item.type.startsWith('image/')) {
      const blob = item.getAsFile()
      if (blob) {
        // Los navegadores pegan imágenes con nombre genérico; lo normalizamos.
        try { blob.name = 'imagen-pegada.' + (item.type.split('/')[1] || 'png') } catch { /* de solo lectura en algunos navegadores */ }
        return blob
      }
    }
  }
  return null
}

async function decodificar(file) {
  // createImageBitmap es más rápido y respeta la orientación EXIF.
  if ('createImageBitmap' in window) return createImageBitmap(file)
  return new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file)
    const img = new Image()
    img.onload = () => { URL.revokeObjectURL(url); resolve(img) }
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error('No se pudo leer la imagen.')) }
    img.src = url
  })
}

function aBlob(canvas, tipo, calidad) {
  return new Promise((resolve) => canvas.toBlob((b) => resolve(b), tipo, calidad))
}

export async function comprimirImagen(file) {
  const error = validarImagen(file)
  if (error) throw new Error(error)
  const bmp = await decodificar(file)
  const w = bmp.width || bmp.naturalWidth
  const h = bmp.height || bmp.naturalHeight
  const escala = Math.min(1, MAX_DIMENSION / Math.max(w, h))
  const nw = Math.max(1, Math.round(w * escala))
  const nh = Math.max(1, Math.round(h * escala))
  const canvas = document.createElement('canvas')
  canvas.width = nw
  canvas.height = nh
  canvas.getContext('2d').drawImage(bmp, 0, 0, nw, nh)
  if (bmp.close) bmp.close()
  // WebP primero; fallback a JPEG si el navegador no lo soporta.
  let blob = await aBlob(canvas, 'image/webp', CALIDAD_WEBP)
  let contentType = 'image/webp'
  if (!blob) {
    blob = await aBlob(canvas, 'image/jpeg', CALIDAD_JPEG)
    contentType = 'image/jpeg'
  }
  if (!blob) throw new Error('El navegador no pudo comprimir la imagen.')
  return { blob, contentType, width: nw, height: nh, antes: file.size, despues: blob.size }
}

export function formatoKB(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}
