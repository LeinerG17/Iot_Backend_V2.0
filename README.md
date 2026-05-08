# Backend IoT — Rutas Universitarias Uniguajira
### Django REST Framework · JWT · Swagger · Python

---

## Instalación

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Autenticación JWT

Todas las rutas requieren un token Bearer en el header:

```
Authorization: Bearer <access_token>
```

### Obtener token
```
POST /api/auth/login/
{ "username": "admin", "password": "tu_password" }
```

### Renovar token
```
POST /api/auth/refresh/
{ "refresh": "<refresh_token>" }
```

---

## Documentación interactiva

| URL | Descripción |
|-----|-------------|
| http://127.0.0.1:8000/api/docs/ | Swagger UI (recomendado) |
| http://127.0.0.1:8000/api/redoc/ | ReDoc |
| http://127.0.0.1:8000/admin/ | Panel de administración |

---

## Endpoints

### Auth
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | /api/auth/login/ | Obtener tokens JWT |
| POST | /api/auth/refresh/ | Renovar access token |
| POST | /api/auth/verify/ | Verificar token |

### Devices
| Método | URL | Descripción |
|--------|-----|-------------|
| GET | /api/devices/ | Listar dispositivos (filtros: tipo, activo, search) |
| POST | /api/devices/register/ | Registrar ESP32 o GPS |
| GET/PUT/DELETE | /api/devices/<id>/ | Detalle, editar o eliminar |

### Readings (GPS)
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | /api/readings/ | ESP32 envía coordenadas |
| GET | /api/readings/list/ | Listar (filtros: device, desde, hasta, velocidad_min) |

### Commands
| Método | URL | Descripción |
|--------|-----|-------------|
| POST | /api/commands/ | Enviar comando al ESP32 |
| GET | /api/commands/list/ | Listar (filtros: device, estado, tipo) |
| GET | /api/commands/latest/?device=<id> | Próximo comando pendiente |

### Recursos (CRUD completo + paginación + filtros)
| URL | Filtros disponibles |
|-----|---------------------|
| /api/conductores/ | search, ordering |
| /api/vehiculos/ | activo, conductor |
| /api/rutas/ | search |
| /api/paradas/ | ruta, search, ordering |
| /api/recorridos/ | vehiculo, ruta, activo |

### Especiales
| Método | URL | Descripción |
|--------|-----|-------------|
| GET | /api/ubicacion/tiempo-real/ | Última ubicación + estado de todos los vehículos |
| GET | /api/rutas/<id>/paradas/ | Ruta con sus paradas ordenadas |

---

## Paginación

Todas las listas usan paginación estándar:

```json
{
  "meta": {
    "total": 50,
    "paginas": 3,
    "pagina_actual": 1,
    "siguiente": "http://...?page=2",
    "anterior": null
  },
  "resultados": [...]
}
```

Parámetros: `?page=2&page_size=10` (máximo 100 por página)

---

## Errores estandarizados

```json
{
  "error": true,
  "codigo": 404,
  "mensaje": "El recurso solicitado no existe.",
  "detalle": { ... }
}
```
