# Módulo: ventas

**Responsable:** Persona C

Registro de ventas; cada venta debe poder generar una factura.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `ventas`)
- `models.py` — modelos SQLAlchemy de este módulo
- `forms.py` — formularios Flask-WTF
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Templates
Los templates HTML de este módulo van en `app/templates/ventas/`.

## Checklist inicial
- [ ] Definir modelo(s) en `models.py`
- [ ] Definir formulario(s) en `forms.py`
- [ ] Implementar rutas CRUD en `routes.py`
- [ ] Crear templates en `app/templates/ventas/`
- [ ] Escribir pruebas en `tests/test_ventas.py`
