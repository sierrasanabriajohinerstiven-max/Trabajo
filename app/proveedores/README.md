# Módulo: proveedores

**Responsable:** Persona B

Alta y gestión de proveedores que abastecen el inventario.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `proveedores`)
- `models.py` — modelo `Proveedor`
- `forms.py` — formularios Flask-WTF (`ProveedorForm`, `EliminarProveedorForm`)
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Modelo `Proveedor`

| Campo | Tipo | Notas |
|---|---|---|
| `id` | Integer | clave primaria |
| `nombre` | String(120) | obligatorio, razón social |
| `nit` | String(30) | obligatorio y **único** (se guarda normalizado, sin puntos ni guiones) |
| `contacto` | String(120) | persona de contacto |
| `email` | String(120) | validado con `email-validator` |
| `telefono` | String(30) | |
| `direccion` | String(200) | |
| `ciudad` | String(80) | |
| `activo` | Boolean | un proveedor se desactiva en vez de borrarse |
| `notas` | Text | |
| `creado_en` / `actualizado_en` | DateTime | se llenan solos |

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/proveedores/` | listado con búsqueda (`?q=`) y filtro (`?estado=activos|inactivos|todos`) |
| GET/POST | `/proveedores/nuevo` | alta de proveedor |
| GET | `/proveedores/<id>` | ficha del proveedor |
| GET/POST | `/proveedores/<id>/editar` | edición |
| POST | `/proveedores/<id>/estado` | activar / desactivar |
| POST | `/proveedores/<id>/eliminar` | borrado definitivo (protegido con CSRF) |

Todas las vistas requieren sesión iniciada (`@login_required`).

## Templates
En `app/templates/proveedores/`: `listado.html`, `formulario.html`, `detalle.html`.
Los estilos propios están en `app/static/css/estilos.css` con el prefijo `.prov-`.

## Checklist inicial
- [x] Definir modelo(s) en `models.py`
- [x] Definir formulario(s) en `forms.py`
- [x] Implementar rutas CRUD en `routes.py`
- [x] Crear templates en `app/templates/proveedores/`
- [x] Escribir pruebas en `tests/test_proveedores.py`
- [ ] Enlazar con Inventario: `Producto.proveedor_id` → `proveedores.id`
      (queda pendiente porque el modelo `Producto` todavía no existe)

## Pendiente de coordinación
- **Inventario**: falta la clave foránea `Producto.proveedor_id`. Los puntos
  exactos donde engancharla están marcados con `TODO (Persona B)` en
  `models.py`, `routes.py` (borrado) y `detalle.html`.
- **Migración**: tras traer estos cambios hay que correr
  `flask db migrate -m "proveedores: modelo Proveedor"` y `flask db upgrade`.
