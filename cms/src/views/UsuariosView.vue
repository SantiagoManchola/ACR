<script setup>
import { onMounted, ref, computed } from 'vue'
import { useUsuariosStore } from '../stores/usuarios'
import { useAuthStore } from '../stores/auth'
import DataTable from '../components/DataTable.vue'
import BaseModal from '../components/BaseModal.vue'
import BaseAlert from '../components/BaseAlert.vue'
import AppIcon from '../components/AppIcon.vue'
import SearchableSelect from '../components/SearchableSelect.vue'
import ConfirmModal from '../components/ConfirmModal.vue'
import PasswordInput from '../components/PasswordInput.vue'
import { apiError } from '../api/http'

const usu = useUsuariosStore()
const auth = useAuthStore()
const tab = ref('usuarios')
const saving = ref(false)

/* Confirmación de acciones destructivas */
const confirmShow = ref(false)
const confirmMsg = ref('')
const pendingToggle = ref(null)
function askToggle(r) {
  if (r.es_superadmin) return
  pendingToggle.value = r
  confirmMsg.value = `¿${r.estado === 'activo' ? 'Inactivar' : 'Activar'} al usuario «${r.nombre}»?`
  confirmShow.value = true
}
async function doToggle() {
  const r = pendingToggle.value
  confirmShow.value = false
  if (!r) return
  const nuevo = r.estado === 'activo' ? 'inactivo' : 'activo'
  await usu.updateUsuario(r.id, { estado: nuevo })
  await usu.loadUsuarios()
  pendingToggle.value = null
}

const rolMap = (id) => usu.roles.find((r) => r.id === id)?.nombre || id
const rolOptions = computed(() => usu.roles.map((r) => ({ value: r.id, label: r.nombre })))

/* Usuarios */
const showUser = ref(false)
const editingUser = ref(null)
const userError = ref('')
const emptyUser = () => ({ nombre: '', identificacion: '', username: '', password: '', rol_id: null })
const userForm = ref(emptyUser())
const userCols = [
  { key: 'nombre', label: 'Nombre', cardTitle: true },
  { key: 'username', label: 'Usuario' },
  { key: 'rol', label: 'Rol', sortValue: (r) => rolMap(r.rol_id) },
  { key: 'estado', label: 'Estado' },
]
function openNewUser() { editingUser.value = null; userForm.value = emptyUser(); userError.value = ''; showUser.value = true }
function openEditUser(r) { editingUser.value = r; userForm.value = { nombre: r.nombre, identificacion: r.identificacion || '', username: r.username, password: '', rol_id: r.rol_id }; userError.value = ''; showUser.value = true }
async function saveUser() {
  userError.value = ''
  if (!userForm.value.nombre || !userForm.value.username || !userForm.value.rol_id) { userError.value = 'Nombre, usuario y rol son obligatorios.'; return }
  if (!editingUser.value && !userForm.value.password) { userError.value = 'La contraseña es obligatoria para nuevos usuarios.'; return }
  saving.value = true
  try {
    const payload = { nombre: userForm.value.nombre, identificacion: userForm.value.identificacion || null, username: userForm.value.username, rol_id: Number(userForm.value.rol_id) }
    if (userForm.value.password) payload.password = userForm.value.password
    if (editingUser.value) await usu.updateUsuario(editingUser.value.id, payload)
    else await usu.createUsuario(payload)
    showUser.value = false; await usu.loadUsuarios()
  } catch (e) { userError.value = apiError(e) } finally { saving.value = false }
}

function refreshUsuarios() { return usu.loadUsuarios() }

/* Roles */
const showRol = ref(false)
const rolError = ref('')
const rolForm = ref({ nombre: '', descripcion: '' })
const rolCols = [
  { key: 'id', label: 'ID', hideOnCard: true },
  { key: 'nombre', label: 'Nombre', cardTitle: true },
  { key: 'descripcion', label: 'Descripción', wide: true },
]
function openNewRol() { rolForm.value = { nombre: '', descripcion: '' }; rolError.value = ''; showRol.value = true }
async function saveRol() {
  rolError.value = ''
  if (!rolForm.value.nombre) { rolError.value = 'El nombre del rol es obligatorio.'; return }
  saving.value = true
  try { await usu.createRol(rolForm.value); showRol.value = false; await usu.loadRoles() }
  catch (e) { rolError.value = apiError(e) } finally { saving.value = false }
}

onMounted(async () => {
  await usu.loadRoles()
  await usu.loadUsuarios()
})
</script>

<template>
  <div class="view-fit">
    <h1>Usuarios y roles</h1>
    <p class="muted">Gestión de accesos del sistema. Solo administradores.</p>

    <div class="tabs">
      <button :class="{ active: tab === 'usuarios' }" @click="tab = 'usuarios'"><AppIcon name="users" />Usuarios</button>
      <button :class="{ active: tab === 'roles' }" @click="tab = 'roles'"><AppIcon name="role" />Roles</button>
    </div>

    <div v-if="tab === 'usuarios'" class="tab-panel">
      <div class="toolbar">
        <button class="btn btn-primary" @click="openNewUser"><AppIcon name="userplus" />Nuevo usuario</button>
        <button class="btn btn-ghost" @click="refreshUsuarios"><AppIcon name="refresh" />Refrescar</button>
      </div>
      <DataTable :columns="userCols" :rows="usu.usuarios" :loading="usu.loading" empty-text="Sin usuarios registrados.">
        <template #cell="{ row, col }">
          <span v-if="col.key === 'rol'">{{ rolMap(row.rol_id) }}</span>
          <span v-else-if="col.key === 'estado'"><span class="badge" :class="row.estado === 'activo' ? 'badge-ok' : 'badge-muted'">{{ row.estado }}</span></span>
          <span v-else>{{ row[col.key] ?? '—' }}</span>
        </template>
        <template #row-actions="{ row }">
          <button class="btn btn-ghost btn-sm" @click="openEditUser(row)"><AppIcon name="edit" :size="16" /></button>
          <button v-if="!row.es_superadmin" class="btn btn-ghost btn-sm" @click="askToggle(row)" title="Activar/Inactivar"><AppIcon :name="row.estado === 'activo' ? 'close' : 'check'" :size="16" /></button>
        </template>
      </DataTable>
    </div>

    <div v-else class="tab-panel">
      <div class="toolbar"><button class="btn btn-primary" @click="openNewRol"><AppIcon name="plus" />Nuevo rol</button></div>
      <DataTable :columns="rolCols" :rows="usu.roles" :loading="usu.loading" empty-text="Sin roles registrados." />
    </div>

    <BaseModal v-model="showUser" :title="editingUser ? 'Editar usuario' : 'Nuevo usuario'">
      <BaseAlert v-if="userError" type="bad" class="mb-1">{{ userError }}</BaseAlert>
      <div class="form-row">
        <div class="field" style="grid-column:span 2"><label>Nombre *</label><input class="input" v-model="userForm.nombre" /></div>
        <div class="field"><label>Identificación</label><input class="input" v-model="userForm.identificacion" /></div>
        <div class="field"><label>Usuario (login) *</label><input class="input" v-model="userForm.username" autocomplete="off" /></div>
        <div class="field"><label>Rol *</label>
          <SearchableSelect v-model="userForm.rol_id" :options="rolOptions" placeholder="Seleccione…" clearable />
        </div>
        <div class="field"><label>{{ editingUser ? 'Nueva contraseña (opcional)' : 'Contraseña *' }}</label>
          <PasswordInput v-model="userForm.password" :required="!editingUser" :placeholder="editingUser ? 'Dejar en blanco para no cambiar' : ''" autocomplete="new-password" />
        </div>
      </div>
      <template #footer>
        <button class="btn btn-ghost" @click="showUser = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveUser">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <BaseModal v-model="showRol" title="Nuevo rol">
      <BaseAlert v-if="rolError" type="bad" class="mb-1">{{ rolError }}</BaseAlert>
      <div class="field"><label>Nombre *</label><input class="input" v-model="rolForm.nombre" placeholder="Ej. operario" /></div>
      <div class="field"><label>Descripción</label><textarea class="textarea" v-model="rolForm.descripcion"></textarea></div>
      <template #footer>
        <button class="btn btn-ghost" @click="showRol = false">Cancelar</button>
        <button class="btn btn-primary" :disabled="saving" @click="saveRol">{{ saving ? 'Guardando…' : 'Guardar' }}</button>
      </template>
    </BaseModal>

    <ConfirmModal v-model:show="confirmShow" title="Cambiar estado de usuario" :message="confirmMsg" confirm-text="Confirmar" danger @confirm="doToggle" />
  </div>
</template>
