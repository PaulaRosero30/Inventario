# 📦 Gestor de Inventarios

Sistema completo de gestión de inventario con backend Python (Flask) y frontend web.

## Estructura del Proyecto

```
inventory_manager/
├── app.py              # Backend API (Flask)
├── requirements.txt    # Dependencias Python
├── index.html          # Frontend web
└── inventory.json      # Base de datos (auto-generada)
```

## Instalación y Uso

### 1. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 2. Iniciar el backend

```bash
python app.py
```

El servidor arrancará en `http://localhost:5000`

### 3. Abrir el frontend

Abre `index.html` en tu navegador (doble clic o arrástralo).

> **Nota:** Para evitar problemas de CORS, se recomienda servirlo con un servidor local:
>
> ```bash
> # Con Python
> python -m http.server 8080
> # Luego abre: http://localhost:8080
> ```

---

## Funcionalidades

- ✅ Dashboard con estadísticas en tiempo real
- ✅ CRUD completo de productos (crear, editar, eliminar)
- ✅ Búsqueda y filtro por categoría
- ✅ Registro de entradas y salidas de stock
- ✅ Historial de movimientos
- ✅ Alertas de stock bajo y sin stock
- ✅ Cálculo de valor total del inventario
- ✅ Datos persistentes en JSON local

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | /api/products | Listar productos |
| POST | /api/products | Crear producto |
| PUT | /api/products/:id | Actualizar producto |
| DELETE | /api/products/:id | Eliminar producto |
| POST | /api/products/:id/movement | Registrar movimiento |
| GET | /api/stats | Estadísticas generales |
| GET | /api/movements | Historial de movimientos |
| GET | /api/categories | Listar categorías |
