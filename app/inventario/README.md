# Módulo: inventario

**Responsable:** Persona B

Control de stock: altas, bajas y ajustes de inventario.

## Estado: implementado

- Listado con buscador (nombre, código o proveedor) y filtro por estado
  (todos / activos / inactivos / stock bajo).
- Alta, edición y borrado de productos.
- Un producto que ya aparece en alguna venta **no se puede borrar**
  (dejaría las ventas sin referencia): se sugiere desactivarlo.
- El SKU es opcional, pero si se usa debe ser único (se guarda en mayúsculas).
- Stock <= `STOCK_BAJO` (5) se resalta en rojo en la tabla.

## Archivos
- `routes.py` — vistas del blueprint `inventario`
- `models.py` — modelo `Producto` (con `buscar()`, `estado` y `valor_en_stock`)
- `forms.py` — `ProductoForm` y `EliminarProductoForm` (CSRF del borrado)

## Diseño
Usa los **componentes compartidos** de `estilos.css` (`.boton`, `.filtros`,
`.tabla-scroll`, `.estado`, `.campo`, `.input`...), que son las mismas reglas
que introdujo el módulo de proveedores con un nombre genérico. Si necesitas
algo propio del módulo, usa el prefijo `.inv-`.

## Pendiente
- [ ] Categorías de producto y unidad de medida
- [ ] Ajuste de stock con motivo (entrada por compra, merma, devolución)
- [ ] Descontar stock automáticamente al registrar una venta (coordinar con Persona C)
