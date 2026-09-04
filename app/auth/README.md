# Módulo: auth

**Responsable:** Persona A

Login cerrado (sin registro público): inicio/cierre de sesión, protección de rutas.

## Archivos
- `routes.py` — vistas/endpoints del módulo (blueprint `auth`)
- `models.py` — modelos SQLAlchemy de este módulo
- `forms.py` — formularios Flask-WTF
- `__init__.py` — registro del blueprint (no tocar la línea de import salvo necesidad real)

## Templates
Los templates HTML de este módulo van en `app/templates/auth/`.

## Checklist inicial
- [ ] Definir modelo(s) en `models.py`
- [ ] Definir formulario(s) en `forms.py`
- [ ] Implementar rutas CRUD en `routes.py`
- [ ] Crear templates en `app/templates/auth/`
- [ ] Escribir pruebas en `tests/test_auth.py`
