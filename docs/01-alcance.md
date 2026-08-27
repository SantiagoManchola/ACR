# Alcance funcional — ACR

> Resumen de módulos, actores y reglas de negocio. Fuente: *Documento de requerimientos*
> y *Listado de requerimientos funcionales y no funcionales* (Proyecto Paz y Región, U. Ibagué).

---

## 1. Actores

| Actor | Rol en el sistema |
|---|---|
| **Administrador** | Control general: usuarios, roles, permisos, consulta total. |
| **Personal administrativo** | Consolida inventario y lecturas de micromedidores. |
| **Operario de planta** | Registra parámetros, dosificaciones, actividades y horas de servicio. |
| **Fontanero** | Toma física de lecturas; entrega info para registro (puede no usar el sistema directo). |

## 2. Módulos y requerimientos (RF)

### Módulo de autenticación y administración
- RF-01 Autenticación · RF-02 Gestión de usuarios · RF-03 Roles · RF-04 Control de permisos ·
  RF-05 Registro de responsable (trazabilidad).

### Módulo de inventario
- RF-06 Registro de elementos · RF-07 Clasificación (categorías/tipos) ·
  RF-08 Ubicación · RF-09 Existencias · RF-10 Entradas · RF-11 Salidas ·
  RF-12 Responsable de salida · RF-13 Motivo de salida · RF-14 Observaciones ·
  RF-15 Historial de movimientos · RF-16 Corrección de registros · RF-17 Inventario mínimo ·
  RF-18 Alertas de existencias · RF-19 Información económica · RF-20 Reporte de inventario.

### Módulo de micromedidores
- RF-21 Suscriptores · RF-22 Micromedidores · RF-23 Info del medidor (serial, tipo, dir., fecha) ·
  RF-24 Asociación suscriptor-medidor · RF-25 Lecturas · RF-26 Fecha de lectura ·
  RF-27 Responsable · RF-28 Lecturas en fechas variables · RF-29 Historial de lecturas ·
  RF-30 Consulta de consumos · RF-31 Consumo promedio (histórico) · RF-32 Novedades ·
  RF-33 Corrección de lecturas · RF-34 Consulta por sector/barrio · RF-35 Reportes de consumo ·
  RF-36 Exportación.

### Módulo de planta de tratamiento
- RF-37 Parámetros · RF-38 Agua cruda · RF-39 Agua tratada · RF-40 Configuración de parámetros ·
  RF-41 Fecha y hora · RF-42 Responsable · RF-43 Dosificación · RF-44 Existencia de químicos ·
  RF-45 Actividades (limpieza, desinfección, tanques, bocatoma) · RF-46 Horas de servicio ·
  RF-47 Observaciones · RF-48 Rangos mín/máx · RF-49 Identificación fuera de rango ·
  RF-50 Acciones correctivas · RF-51 Historial · RF-52 Consulta histórica ·
  RF-53 Reporte de planta · RF-54 Exportación de planta.

### Módulo de consultas y reportes
- Históricos filtrables por fecha/sector/parámetro + exportación (CSV/Excel/PDF).

## 3. Requerimientos no funcionales (RNF) destacados
RNF-01 Acceso web · RNF-02 Disponibilidad 24/7 · RNF-03 Seguridad (auth) ·
RNF-04 Control de acceso por rol · RNF-05 Protección de info sensible (planta) ·
RNF-06 Integridad · RNF-07 Trazabilidad · RNF-08 Usabilidad · RNF-09 Adaptabilidad (móvil) ·
RNF-10 Rendimiento · RNF-11 Escalabilidad (~1.124→más medidores) · RNF-12 Mantenibilidad modular ·
RNF-13 Configurabilidad · RNF-14 Persistencia · RNF-15 Respaldo · RNF-16 Recuperación ·
RNF-17 Compatibilidad (navegadores modernos) · RNF-18 Documentación · RNF-19 Exportación.

## 4. Reglas de negocio (clave)
1. Lecturas de micromedidores: periodicidad mensual.
2. Sin lectura → usar promedio histórico según procedimiento de la org.
3. Lecturas irregulares: identificar y validar posteriormente.
4. Cada lectura asociada a usuario, micromedidor y responsable.
5. Inventario diferencia elementos fijos vs accesorios/consumo.
6. Entradas/salidas de accesorios afectan existencias.
7. Movimientos conservan elemento, cuándo y quién.
8. Planta mide parámetros diariamente (varias veces al día).
9. Parámetros pueden tener min/máx definidos.
10. Fuera de rango → registrar acción correctiva.
11. Dosificación registra producto y cantidad.
12. Info de planta con mayores restricciones de acceso.
13. Modificaciones/eliminaciones restringidas a autorizados.
14. Históricos se conservan para consulta y reportes.

## 5. Priorización
- **Alta:** auth/usuarios, inventario básico, entradas/salidas, suscriptores/medidores,
  lecturas, histórico de consumos, parámetros de planta, dosificaciones, actividades de
  planta, históricos, control de permisos.
- **Media:** alertas de inventario/parámetros, reportes consolidados, exportación, acciones
  correctivas, consulta por sector, gestión de químicos.
- **Futuro:** niveles de tanques, estado de red, PQR, presiones, purgas, integración con
  facturación, captura automática desde dispositivos.
