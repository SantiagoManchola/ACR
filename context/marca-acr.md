# Contexto de marca — Acueducto Comunitario Acuaricaurte (ACR)

> Documento de investigación y definición de marca. Base para la identidad visual de todo
> el sistema (API, CMS y documentación).

---

## 1. ¿Qué es Acuaricaurte?

El **Acueducto Comunitario Acuaricaurte** es una empresa comunitaria de agua del
**barrio Ricaurte, ciudad de Ibagué, departamento del Tolima, Colombia**.

- **Origen:** iniciativa vecinal de autogestión del agua, surgida por la ausencia o
  insuficiencia de cobertura estatal en el sector.
- **Fuente de captación:** la **quebrada El Tejar**, en la parte alta del barrio.
- **Población atendida (según fuentes académicas):** aproximadamente **1.380 matrículas**,
  lo que equivale a cerca de **8.000 personas**. El sistema de facturación interno reporta
  cerca de **1.124 usuarios** registrados, de los cuales solo una parte cuenta hoy con
  micromedidores instalados.
- **Proceso de potabilización:** captación → desarenado → coagulación → floculación →
  sedimentación → desinfección → almacenamiento → distribución.
- **Problemáticas históricas documentadas:** pérdidas de agua, turbiedad de la fuente,
  falta de potabilización adecuada, mora en el pago de tarifas, y dependencia de registros
  manuales (formatos físicos, Excel y WhatsApp).

## 2. Personalidad de marca

| Atributo | Descripción |
|---|---|
| Misión | Llevar agua potable y gestionar el recurso hídrico de forma comunitaria y transparente. |
| Valores | Servicio público, comunidad, transparencia, mejora continua, cuidado del agua. |
| Tono | Cercano, institucional, confiable, sencillo (los usuarios tienen distintos niveles tecnológicos). |
| Promesa | Información operativa centralizada, trazable y disponible para la toma de decisiones. |

## 3. Identidad visual

### Colores

| Rol | Color | HEX | Uso |
|---|---|---|---|
| **Primario** | Azul Acuaricaurte | `#2160AD` | Cabeceras, botones primarios, marca, enlaces, acentos. |
| **Secundario / fondo** | Blanco | `#FFFFFF` | Fondos, superficies de tarjetas, texto sobre azul. |
| **Acento neutro (sugerido)** | Gris azulado | `#EAF1FB` | Fondos suaves, filas alternas de tablas. |
| **Texto** | Casi negro azulado | `#1B2733` | Cuerpo de texto. |
| **Estado (sugerido)** | Verde / ámbar / rojo | `#2E9E5B` / `#E0A106` / `#D64545` | Éxito, advertencia, fuera de rango. |

> Regla de marca: **predominio azul `#2160AD` + blanco**. El azul comunica agua, confianza
> e institucionalidad; el blanco aporta claridad y limpieza. Evitar saturar con otros colores
> salvo para semáforos de estado (alertas de inventario y parámetros fuera de rango).

### Tipografía (sugerida)

- **Títulos / marca:** sans-serif limpia (p. ej. *Inter*, *Poppins* o *Montserrat*).
- **Cuerpo / datos:** sans-serif legible en tablas (p. ej. *Inter*, *Roboto*).
- Priorizar legibilidad en pantallas pequeñas (fontaneros y operarios usan móviles).

### Logotipo (a definir / sugerido)

- Concepto: gota de agua estilizada + onda (quebrada) sobre fondo azul, o iniciales
  **ACR** en blanco sobre azul `#2160AD`.
- No se cuenta hoy con un archivo vectorial oficial; el CMS/API usarán el color y el
  nombre como identidad mínima hasta disponer del isometric/logo final.

## 4. Aplicación en el software

- **API:** respuestas JSON neutras; el color de marca vive en el CMS (HTML/CSS).
- **CMS:** tema con variable CSS `--acr-azul: #2160AD` y `--acr-blanco: #FFFFFF`.
  Cabecera azul, botones primarios azules, fondo blanco, acentos en gris azulado.
- **Documentación:** mantener la misma paleta en diagramas y portadas.

## 5. Fuentes de la investigación

- RedCOL / Universidad de Ibagué: *Plan de reducción de pérdidas acueducto comunitario
  Acuaricaurte* (2025); *Modelo de gestión administrativo Acuaricaurte basado en TPS* (2022);
  *Diagnóstico de la planta de tratamiento de Acuaricaurte*.
- IBAL (Empresa Ibaguereña de Acueducto y Alcantarillado): nota pública de acompañamiento
  a la potabilización (2022).
- Prensa local (El Nuevo Día): cobertura de la operación y la quebrada El Tejar.
- Documentación interna del proyecto: *Documento de requerimientos del sistema* y
  *Listado de requerimientos funcionales y no funcionales* (Proyecto Paz y Región,
  Universidad de Ibagué, 21 ago 2026).
