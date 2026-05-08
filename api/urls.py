from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'roles', views.RolViewSet)
router.register(r'usuario-roles', views.UsuarioRolViewSet)
router.register(r'conductores', views.ConductorViewSet)
router.register(r'rutas', views.RutaViewSet)
router.register(r'paradas', views.ParadaViewSet)
router.register(r'ruta-paradas', views.RutaParadaViewSet)
router.register(r'vehiculos', views.VehiculoViewSet)
router.register(r'asignaciones', views.AsignacionRutaViewSet)
router.register(r'horarios', views.HorarioRutaViewSet)
router.register(r'estados-operacion', views.EstadoOperacionViewSet)
router.register(r'respuestas-comando', views.RespuestaComandoViewSet)
router.register(r'auditorias', views.AuditoriaSistemaViewSet)
# Nuevos
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'recursos', views.RecursoViewSet)
router.register(r'rol-recursos', views.RolRecursoViewSet)
router.register(r'perfiles', views.PerfilUsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # ── DEVICES ──────────────────────────────────────────────────
    path('devices/', views.get_devices),
    path('devices/register/', views.register_device),
    path('devices/<int:pk>/', views.device_detail),

    # ── READINGS ─────────────────────────────────────────────────
    path('readings/', views.post_reading),
    path('readings/list/', views.get_readings),

    # ── COMMANDS ─────────────────────────────────────────────────
    path('commands/', views.post_command),
    path('commands/list/', views.get_commands),
    path('commands/latest/', views.get_commands_latest),

    # ── ALERTAS ──────────────────────────────────────────────────
    path('alertas/', views.get_alertas),

    # ── ESPECIALES ───────────────────────────────────────────────
    path('ubicacion/tiempo-real/', views.ubicacion_tiempo_real),
    path('rutas/<int:pk>/paradas/', views.ruta_con_paradas),

    path('estudiante/rutas/', views.rutas_estudiante),
]
