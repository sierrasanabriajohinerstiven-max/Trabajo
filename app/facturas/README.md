# Módulo: facturas

**Responsable:** Persona A

Emisión y consulta de facturas, generadas a partir de una venta.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `facturas`)
- `models.py` — modelos SQLAlchemy de este módulo
- `forms.py` — formularios Flask-WTF
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Templates
Los templates HTML de este módulo van en `app/templates/facturas/`.

## Checklist inicial
- [ ] Definir modelo(s) en `models.py`
- [ ] Definir formulario(s) en `forms.py`
- [ ] Implementar rutas CRUD en `routes.py`
- [ ] Crear templates en `app/templates/facturas/`
- [ ] Escribir pruebas en `tests/test_facturas.py`
