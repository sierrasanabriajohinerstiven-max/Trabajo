# Sistema de Facturas, Inventario, Ventas y Proveedores

Aplicación web hecha con **Flask (Python)**. Login cerrado (no hay registro
público de usuarios; se crean por un admin o un script de seed).

Base de datos: **SQLite local** gestionada con SQLAlchemy (archivo en
`instance/app.db`, no se sube al repo).

## Puesta en marcha

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env        # y completar SECRET_KEY
flask db init                 # solo la primera vez
flask db migrate -m "inicial"
flask db upgrade
python run.py
```

## División del equipo (3 personas)

| Persona | Módulos | Carpetas principales |
|---|---|---|
| **Persona A** | Login (auth) + Facturas | `app/auth/`, `app/facturas/` |
| **Persona B** | Inventario + Proveedores | `app/inventario/`, `app/proveedores/` |
| **Persona C** | Ventas | `app/ventas/` |

Razón de la agrupación: Proveedores abastece directamente el Inventario
(misma persona, menos fricción de coordinación). Ventas queda como módulo
independiente para Persona C, y se conectará por clave foránea tanto con
Inventario (qué producto se vendió) como con Facturas (persona A genera la
factura a partir de la venta) — esa conexión es el principal punto de
coordinación entre los 3.

Cada módulo tiene su propio `README.md` con checklist (ej.
[app/auth/README.md](app/auth/README.md)).

## Estructura del proyecto

```
app/
├── __init__.py          # app factory: registra los 5 blueprints (tocar con cuidado, es compartido)
├── config.py             # configuración (lee .env)
├── extensions.py         # db, login_manager, migrate (compartido)
├── models/
│   └── usuario.py         # modelo Usuario, compartido (login)
├── auth/                  # Persona A — login cerrado
├── facturas/               # Persona A
├── inventario/              # Persona B
├── proveedores/              # Persona B
├── ventas/                     # Persona C
├── static/{css,js,img}
└── templates/
    ├── base.html          # layout común (compartido, tocar con cuidado)
    └── <modulo>/           # un template por módulo

instance/    # aquí Flask crea app.db (SQLite local, ignorado por git)
migrations/  # generado por flask-migrate
tests/       # un archivo de pruebas por módulo
```

Cada blueprint (`auth`, `facturas`, `inventario`, `proveedores`, `ventas`)
sigue la misma forma interna:

- `__init__.py` — registra el Blueprint (no tocar salvo necesidad real)
- `models.py` — modelos SQLAlchemy propios del módulo
- `forms.py` — formularios Flask-WTF
- `routes.py` — vistas/endpoints

Esto permite que cada persona trabaje casi siempre dentro de su propia
carpeta, minimizando conflictos de merge. Los únicos archivos **compartidos**
(coordinar antes de tocarlos) son:

- `app/__init__.py`
- `app/extensions.py`, `app/config.py`
- `app/models/usuario.py`
- `app/templates/base.html`

## Esquema de datos (contrato compartido)

Los modelos base ya están definidos para que el resumen del panel pueda
calcular sus indicadores. **No los redefinas**: constrúyele encima (agrega
campos, validaciones, CRUD). Si necesitas renombrar una tabla o una clave,
avisa al equipo antes.

| Modelo | Archivo | Dueño |
|---|---|---|
| `Usuario` | `app/models/usuario.py` | compartido |
| `Proveedor` | `app/proveedores/models.py` | Persona B |
| `Producto` | `app/inventario/models.py` | Persona B |
| `Venta`, `DetalleVenta` | `app/ventas/models.py` | Persona C |
| `Factura` | `app/facturas/models.py` | Persona A |

Relaciones: `Proveedor 1—N Producto` · `Venta 1—N DetalleVenta N—1 Producto`
· `Venta 1—1 Factura` · `Venta N—1 Usuario`.

El resumen del panel (`app/main/services.py`) consulta estas tablas para
calcular ventas del mes, productos más vendidos y valor del inventario.

## Primeras tareas de cada persona

- **Persona A**: implementar el `login` real en `app/auth/routes.py` — hoy
  es un placeholder sin formulario, así que **nadie puede entrar al sistema
  todavía** (todas las vistas son `@login_required`). El `logout` ya
  funciona. Después, CRUD de `Factura`.
- **Persona B**: CRUD de `Producto` en `app/inventario/` y de `Proveedor`
  en `app/proveedores/` (un proveedor abastece varios productos).
- **Persona C**: CRUD de `Venta` en `app/ventas/` (una venta descuenta
  stock del Producto y debe poder generar una Factura).

## Convenciones

- Commits: mencionar el módulo, ej. `facturas: agrega validación de RUC`.
- Cada `TODO (Persona X)` en el código marca quién es responsable de esa
  parte.
