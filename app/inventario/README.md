# Módulo: inventario

**Responsable:** Persona B

Control de stock: altas, bajas y ajustes de inventario.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `inventario`)
- `models.py` — modelos SQLAlchemy de este módulo
- `forms.py` — formularios Flask-WTF
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Templates
Los templates HTML de este módulo van en `app/templates/inventario/`.

## Checklist inicial
- [ ] Definir modelo(s) en `models.py`
- [ ] Definir formulario(s) en `forms.py`
- [ ] Implementar rutas CRUD en `routes.py`
- [ ] Crear templates en `app/templates/inventario/`
- [ ] Escribir pruebas en `tests/test_inventario.py`
