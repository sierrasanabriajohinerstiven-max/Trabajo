# Módulo: proveedores

**Responsable:** Persona B

Alta y gestión de proveedores que abastecen el inventario.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `proveedores`)
- `models.py` — modelos SQLAlchemy de este módulo
- `forms.py` — formularios Flask-WTF
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Templates
Los templates HTML de este módulo van en `app/templates/proveedores/`.

## Checklist inicial
- [ ] Definir modelo(s) en `models.py`
- [ ] Definir formulario(s) en `forms.py`
- [ ] Implementar rutas CRUD en `routes.py`
- [ ] Crear templates en `app/templates/proveedores/`
- [ ] Escribir pruebas en `tests/test_proveedores.py`
