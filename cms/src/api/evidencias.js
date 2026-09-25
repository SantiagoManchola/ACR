import client from './http'
import { comprimirImagen } from '../utils/imagen'

// Pide al API una URL firmada PUT para subida directa del navegador a R2.
// (R2 NO soporta subidas POST: responde 501. Por eso se usa PUT firmado.)
export async function pedirPresign(modulo, contentType) {
  const { data } = await client.post('/evidencias/presign', { modulo, content_type: contentType })
  return data // { url, key, content_type, public_url, expires_in, tamano_maximo_bytes }
}

// Sube el blob ya comprimido directo a R2 con PUT.
// El header Content-Type debe coincidir con el firmado (si no, R2 da 403).
// Se usa fetch para no enviar el header Authorization al bucket.
export async function subirAR2(presign, blob, contentType) {
  const resp = await fetch(presign.url, {
    method: 'PUT',
    body: blob,
    headers: { 'Content-Type': contentType || presign.content_type },
  })
  if (!resp.ok) throw new Error('No se pudo subir la foto al almacenamiento (R2).')
  return presign.public_url
}

// Confirma en el API que el objeto quedó en R2 y cumple el tamaño máximo.
export async function confirmarEvidencia(key) {
  const { data } = await client.post('/evidencias/confirmar', { key })
  return data
}

// Flujo completo: comprimir -> firmar -> subir (PUT) -> confirmar.
// Devuelve { public_url, stats }.
export async function subirEvidencia(modulo, file, onPaso) {
  const comp = await comprimirImagen(file)
  onPaso?.('Preparando foto…')
  const presign = await pedirPresign(modulo, comp.contentType)
  onPaso?.('Subiendo foto…')
  const publicUrl = await subirAR2(presign, comp.blob, comp.contentType)
  onPaso?.('Terminando…')
  await confirmarEvidencia(presign.key)
  return { public_url: publicUrl, stats: comp }
}
