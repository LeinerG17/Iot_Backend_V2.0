from django.contrib import admin
from .models import (
    Rol, UsuarioRol, Conductor, Ruta, Parada, RutaParada,
    Vehiculo, DispositivoIot, AsignacionRuta, HorarioRuta,
    UbicacionGps, HistorialRecorrido, EstadoOperacion,
    ComandoRemoto, RespuestaComando, AlertaSistema, AuditoriaSistema
)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'creado_en']
    search_fields = ['nombre']


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'asignado_en']
    list_filter = ['rol']
    search_fields = ['usuario__username']


@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'cedula', 'telefono', 'licencia', 'activo', 'creado_en']
    search_fields = ['nombre', 'cedula']
    list_filter = ['activo']
    ordering = ['nombre']


@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activa', 'creado_en']
    search_fields = ['nombre']
    list_filter = ['activa']


@admin.register(Parada)
class ParadaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'latitud', 'longitud', 'creado_en']
    search_fields = ['nombre']


@admin.register(RutaParada)
class RutaParadaAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'parada', 'orden']
    list_filter = ['ruta']
    ordering = ['ruta', 'orden']


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['placa', 'modelo', 'capacidad', 'activo', 'creado_en']
    search_fields = ['placa', 'modelo']
    list_filter = ['activo']


@admin.register(DispositivoIot)
class DispositivoIotAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'identificador', 'vehiculo', 'activo', 'ultima_conexion']
    search_fields = ['nombre', 'identificador']
    list_filter = ['tipo', 'activo']


@admin.register(AsignacionRuta)
class AsignacionRutaAdmin(admin.ModelAdmin):
    list_display = ['conductor', 'vehiculo', 'ruta', 'fecha_inicio', 'fecha_fin', 'activa']
    list_filter = ['activa', 'ruta']
    search_fields = ['conductor__nombre', 'vehiculo__placa']


@admin.register(HorarioRuta)
class HorarioRutaAdmin(admin.ModelAdmin):
    list_display = ['ruta', 'dia_semana', 'hora_salida', 'hora_llegada_estimada', 'activo']
    list_filter = ['ruta', 'dia_semana', 'activo']


@admin.register(UbicacionGps)
class UbicacionGpsAdmin(admin.ModelAdmin):
    list_display = ['dispositivo', 'latitud', 'longitud', 'velocidad', 'timestamp']
    list_filter = ['dispositivo']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(HistorialRecorrido)
class HistorialRecorridoAdmin(admin.ModelAdmin):
    list_display = ['id', 'asignacion', 'inicio', 'fin', 'activo']
    list_filter = ['activo']
    readonly_fields = ['inicio']
    ordering = ['-inicio']


@admin.register(EstadoOperacion)
class EstadoOperacionAdmin(admin.ModelAdmin):
    list_display = ['vehiculo', 'estado', 'descripcion', 'registrado_en']
    list_filter = ['estado', 'vehiculo']
    ordering = ['-registrado_en']


@admin.register(ComandoRemoto)
class ComandoRemotoAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'dispositivo', 'estado', 'creado_en', 'ejecutado_en']
    list_filter = ['tipo', 'estado']
    readonly_fields = ['creado_en']
    ordering = ['-creado_en']


@admin.register(RespuestaComando)
class RespuestaComandoAdmin(admin.ModelAdmin):
    list_display = ['comando', 'exitoso', 'mensaje', 'recibido_en']
    list_filter = ['exitoso']
    readonly_fields = ['recibido_en']


@admin.register(AlertaSistema)
class AlertaSistemaAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'nivel', 'dispositivo', 'vehiculo', 'resuelta', 'creado_en']
    list_filter = ['tipo', 'nivel', 'resuelta']
    search_fields = ['mensaje']
    ordering = ['-creado_en']


@admin.register(AuditoriaSistema)
class AuditoriaSistemaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'accion', 'tabla_afectada', 'registro_id', 'ip', 'creado_en']
    list_filter = ['tabla_afectada']
    search_fields = ['usuario__username', 'accion']
    readonly_fields = ['creado_en']
    ordering = ['-creado_en']

from .models import Recurso, RolRecurso, PerfilUsuario

@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'ruta', 'icono', 'orden', 'activo']
    list_filter = ['activo']
    ordering = ['orden']

@admin.register(RolRecurso)
class RolRecursoAdmin(admin.ModelAdmin):
    list_display = ['rol', 'recurso']
    list_filter = ['rol']

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'telefono', 'estado', 'creado_en']
    list_filter = ['estado']
    search_fields = ['usuario__username']
