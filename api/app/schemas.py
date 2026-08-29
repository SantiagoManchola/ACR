"""Esquemas Pydantic v2 para validación de entrada/salida (RNF-06)."""
from datetime import date, datetime, time
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field

from .config import settings
from .models import (
    CategoriaTipo,
    EstadoRegistro,
    TipoAgua,
    TipoMovimiento,
    TipoUsuario,
)

# Base común con from_attributes (ORM mode)
class _ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ----------------------------- Tokens / auth ---------------------------------
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class CambioPassword(BaseModel):
    password_actual: str
    password_nuevo: str = Field(min_length=6)


# ----------------------------- Roles / permisos ------------------------------
class RolOut(_ORM):
    id: int
    nombre: str
    descripcion: Optional[str] = None


class RolCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=50)
    descripcion: Optional[str] = None


# ----------------------------- Usuarios --------------------------------------
class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    identificacion: Optional[str] = None
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6)
    rol_id: int


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
    rol_id: Optional[int] = None
    estado: Optional[EstadoRegistro] = None


class UsuarioOut(_ORM):
    id: int
    nombre: str
    identificacion: Optional[str] = None
    username: str
    rol_id: int
    rol: Optional[RolOut] = None
    estado: EstadoRegistro
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def es_superadmin(self) -> bool:
        return self.username == settings.admin_username


# ----------------------------- Inventario ------------------------------------
class CategoriaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    tipo: CategoriaTipo
    descripcion: Optional[str] = None


class CategoriaOut(_ORM):
    id: int
    nombre: str
    tipo: CategoriaTipo
    descripcion: Optional[str] = None


class ElementoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    categoria_id: int
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    cantidad: Decimal = Field(default=0, ge=0)
    unidad: Optional[str] = None
    proveedor: Optional[str] = None
    valor: Optional[Decimal] = None
    minimo: Optional[Decimal] = None
    observaciones: Optional[str] = None


class ElementoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    cantidad: Optional[Decimal] = None
    unidad: Optional[str] = None
    proveedor: Optional[str] = None
    valor: Optional[Decimal] = None
    minimo: Optional[Decimal] = None
    estado: Optional[EstadoRegistro] = None
    observaciones: Optional[str] = None


class ElementoOut(_ORM):
    id: int
    nombre: str
    categoria_id: int
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    cantidad: Decimal
    unidad: Optional[str] = None
    proveedor: Optional[str] = None
    valor: Optional[Decimal] = None
    minimo: Optional[Decimal] = None
    estado: EstadoRegistro
    observaciones: Optional[str] = None


class MovimientoCreate(BaseModel):
    cantidad: Decimal = Field(gt=0)
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None


class MovimientoOut(_ORM):
    id: int
    elemento_id: int
    tipo: TipoMovimiento
    cantidad: Decimal
    responsable_id: Optional[int] = None
    motivo: Optional[str] = None
    observaciones: Optional[str] = None
    fecha: date
    hora: Optional[time] = None


class AlertaOut(BaseModel):
    """Elemento de inventario o químico por debajo de su mínimo configurado."""

    tipo: str
    id: int
    nombre: str
    categoria: str
    cantidad: Decimal
    minimo: Optional[Decimal] = None
    unidad: Optional[str] = None


# ----------------------------- Micromedidores --------------------------------
class SuscriptorCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=150)
    identificacion: Optional[str] = None
    codigo_usuario: Optional[str] = None
    codigo_facturacion: Optional[str] = None
    tipo_usuario: TipoUsuario = TipoUsuario.residencial
    sector: Optional[str] = None
    direccion: Optional[str] = None


class SuscriptorUpdate(BaseModel):
    nombre: Optional[str] = None
    identificacion: Optional[str] = None
    codigo_usuario: Optional[str] = None
    codigo_facturacion: Optional[str] = None
    tipo_usuario: Optional[TipoUsuario] = None
    sector: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[EstadoRegistro] = None


class SuscriptorOut(_ORM):
    id: int
    nombre: str
    identificacion: Optional[str] = None
    codigo_usuario: Optional[str] = None
    codigo_facturacion: Optional[str] = None
    tipo_usuario: TipoUsuario
    sector: Optional[str] = None
    direccion: Optional[str] = None
    estado: EstadoRegistro


class MicromedidorCreate(BaseModel):
    serial: str = Field(min_length=1, max_length=50)
    tipo: Optional[str] = None
    suscriptor_id: Optional[int] = None
    direccion: Optional[str] = None
    fecha_instalacion: Optional[date] = None


class MicromedidorUpdate(BaseModel):
    serial: Optional[str] = None
    tipo: Optional[str] = None
    suscriptor_id: Optional[int] = None
    direccion: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    estado: Optional[EstadoRegistro] = None


class MicromedidorOut(_ORM):
    id: int
    serial: str
    tipo: Optional[str] = None
    suscriptor_id: Optional[int] = None
    direccion: Optional[str] = None
    fecha_instalacion: Optional[date] = None
    estado: EstadoRegistro


class LecturaCreate(BaseModel):
    micromedidor_id: int
    suscriptor_id: int
    fecha: Optional[date] = None
    hora: Optional[time] = None
    lectura: Decimal
    responsable_id: Optional[int] = None
    novedad: Optional[str] = None
    irregular: bool = False


class LecturaOut(_ORM):
    id: int
    micromedidor_id: int
    suscriptor_id: int
    fecha: date
    hora: Optional[time] = None
    lectura: Decimal
    consumo: Optional[Decimal] = None
    promedio_usado: bool
    responsable_id: Optional[int] = None
    novedad: Optional[str] = None
    irregular: bool


# ----------------------------- Planta ----------------------------------------
class ParametroCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    tipo_agua: TipoAgua
    unidad: Optional[str] = None
    valor_min: Optional[Decimal] = None
    valor_max: Optional[Decimal] = None


class ParametroUpdate(BaseModel):
    nombre: Optional[str] = None
    tipo_agua: Optional[TipoAgua] = None
    unidad: Optional[str] = None
    valor_min: Optional[Decimal] = None
    valor_max: Optional[Decimal] = None
    estado: Optional[EstadoRegistro] = None


class ParametroOut(_ORM):
    id: int
    nombre: str
    tipo_agua: TipoAgua
    unidad: Optional[str] = None
    valor_min: Optional[Decimal] = None
    valor_max: Optional[Decimal] = None
    estado: EstadoRegistro


class MedicionCreate(BaseModel):
    parametro_id: int
    valor: Decimal
    fecha: Optional[date] = None
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    accion_correctiva: Optional[str] = None
    observaciones: Optional[str] = None


class MedicionOut(_ORM):
    id: int
    parametro_id: int
    valor: Decimal
    fecha: date
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    fuera_rango: bool
    accion_correctiva: Optional[str] = None
    observaciones: Optional[str] = None


class DosificacionCreate(BaseModel):
    elemento_id: int
    cantidad: Decimal = Field(gt=0)
    fecha: Optional[date] = None
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None


class DosificacionOut(_ORM):
    id: int
    elemento_id: int
    cantidad: Decimal
    unidad: Optional[str] = None
    fecha: date
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None


class ActividadCreate(BaseModel):
    tipo: str = Field(min_length=1, max_length=80)
    fecha: Optional[date] = None
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None
    evidencia: Optional[str] = None


class ActividadUpdate(BaseModel):
    tipo: Optional[str] = None
    fecha: Optional[date] = None
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    estado: Optional[EstadoRegistro] = None
    observaciones: Optional[str] = None
    evidencia: Optional[str] = None


class ActividadOut(_ORM):
    id: int
    tipo: str
    fecha: date
    hora: Optional[time] = None
    responsable_id: Optional[int] = None
    estado: EstadoRegistro
    observaciones: Optional[str] = None
    evidencia: Optional[str] = None


class HoraServicioCreate(BaseModel):
    fecha: Optional[date] = None
    horas: Decimal = Field(gt=0)
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None


class HoraServicioOut(_ORM):
    id: int
    fecha: date
    horas: Decimal
    responsable_id: Optional[int] = None
    observaciones: Optional[str] = None
