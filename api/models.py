from django.db import models
from django.contrib.auth.models import User


# ─── ROL ─────────────────────────────────────────────────────────────────────
class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


# ─── USUARIO_ROL ──────────────────────────────────────────────────────────────
class UsuarioRol(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='usuarios')
    asignado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'usuario_rol'
        verbose_name = 'Usuario Rol'
        verbose_name_plural = 'Usuarios Roles'
        unique_together = ('usuario', 'rol')

    def __str__(self):
        return f"{self.usuario.username} → {self.rol.nombre}"


# ─── CONDUCTOR ────────────────────────────────────────────────────────────────
class Conductor(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='conductor')
    nombre = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    licencia = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conductor'
        verbose_name = 'Conductor'
        verbose_name_plural = 'Conductores'

    def __str__(self):
        return f"{self.nombre} ({self.cedula})"


# ─── RUTA ─────────────────────────────────────────────────────────────────────
class Ruta(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ruta'
        verbose_name = 'Ruta'
        verbose_name_plural = 'Rutas'

    def __str__(self):
        return self.nombre


# ─── PARADA ───────────────────────────────────────────────────────────────────
class Parada(models.Model):
    nombre = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()
    descripcion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parada'
        verbose_name = 'Parada'
        verbose_name_plural = 'Paradas'

    def __str__(self):
        return self.nombre


# ─── RUTA_PARADA ──────────────────────────────────────────────────────────────
class RutaParada(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='ruta_paradas')
    parada = models.ForeignKey(Parada, on_delete=models.CASCADE, related_name='ruta_paradas')
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'ruta_parada'
        verbose_name = 'Ruta Parada'
        verbose_name_plural = 'Rutas Paradas'
        unique_together = ('ruta', 'parada')
        ordering = ['orden']

    def __str__(self):
        return f"{self.ruta.nombre} → {self.parada.nombre} (#{self.orden})"


# ─── VEHÍCULO ─────────────────────────────────────────────────────────────────
class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    capacidad = models.IntegerField()
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vehiculo'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return self.placa


# ─── DISPOSITIVO_IOT ──────────────────────────────────────────────────────────
TIPO_DISPOSITIVO = [
    ('ESP32', 'ESP32'),
    ('GPS_NEO6M', 'GPS NEO-6M'),
]

class DispositivoIot(models.Model):
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_DISPOSITIVO, default='ESP32')
    identificador = models.CharField(max_length=100, unique=True, help_text='MAC o ID único')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispositivos')
    activo = models.BooleanField(default=True)
    ultima_conexion = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'dispositivo_iot'
        verbose_name = 'Dispositivo IoT'
        verbose_name_plural = 'Dispositivos IoT'

    def __str__(self):
        return f"{self.nombre} [{self.tipo}]"


# ─── ASIGNACION_RUTA ──────────────────────────────────────────────────────────
class AsignacionRuta(models.Model):
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='asignaciones')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='asignaciones')
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='asignaciones')
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'asignacion_ruta'
        verbose_name = 'Asignación de Ruta'
        verbose_name_plural = 'Asignaciones de Rutas'

    def __str__(self):
        return f"{self.conductor.nombre} | {self.vehiculo.placa} | {self.ruta.nombre}"


# ─── HORARIO_RUTA ─────────────────────────────────────────────────────────────
DIAS_SEMANA = [
    ('lunes', 'Lunes'),
    ('martes', 'Martes'),
    ('miercoles', 'Miércoles'),
    ('jueves', 'Jueves'),
    ('viernes', 'Viernes'),
    ('sabado', 'Sábado'),
    ('domingo', 'Domingo'),
]

class HorarioRuta(models.Model):
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE, related_name='horarios')
    dia_semana = models.CharField(max_length=15, choices=DIAS_SEMANA)
    hora_salida = models.TimeField()
    hora_llegada_estimada = models.TimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'horario_ruta'
        verbose_name = 'Horario de Ruta'
        verbose_name_plural = 'Horarios de Rutas'

    def __str__(self):
        return f"{self.ruta.nombre} | {self.dia_semana} {self.hora_salida}"


# ─── UBICACION_GPS ────────────────────────────────────────────────────────────
class UbicacionGps(models.Model):
    dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, related_name='ubicaciones')
    latitud = models.FloatField()
    longitud = models.FloatField()
    velocidad = models.FloatField(default=0.0, help_text='km/h')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ubicacion_gps'
        verbose_name = 'Ubicación GPS'
        verbose_name_plural = 'Ubicaciones GPS'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.dispositivo.nombre} @ {self.timestamp}"


# ─── HISTORIAL_RECORRIDO ──────────────────────────────────────────────────────
class HistorialRecorrido(models.Model):
    asignacion = models.ForeignKey(AsignacionRuta, on_delete=models.CASCADE, related_name='recorridos')
    inicio = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)

    class Meta:
        db_table = 'historial_recorrido'
        verbose_name = 'Historial de Recorrido'
        verbose_name_plural = 'Historial de Recorridos'
        ordering = ['-inicio']

    def __str__(self):
        return f"Recorrido {self.id} | {self.asignacion}"


# ─── ESTADO_OPERACION ─────────────────────────────────────────────────────────
ESTADO_CHOICES = [
    ('activo', 'Activo'),
    ('inactivo', 'Inactivo'),
    ('mantenimiento', 'En Mantenimiento'),
    ('fuera_servicio', 'Fuera de Servicio'),
]

class EstadoOperacion(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='estados')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    descripcion = models.TextField(blank=True)
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'estado_operacion'
        verbose_name = 'Estado de Operación'
        verbose_name_plural = 'Estados de Operación'
        ordering = ['-registrado_en']

    def __str__(self):
        return f"{self.vehiculo.placa} → {self.estado}"


# ─── COMANDO_REMOTO ───────────────────────────────────────────────────────────
TIPO_COMANDO = [
    ('activar', 'Activar'),
    ('desactivar', 'Desactivar'),
]

ESTADO_COMANDO = [
    ('pendiente', 'Pendiente'),
    ('enviado', 'Enviado'),
    ('ejecutado', 'Ejecutado'),
    ('fallido', 'Fallido'),
]

class ComandoRemoto(models.Model):
    dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.CASCADE, related_name='comandos')
    tipo = models.CharField(max_length=15, choices=TIPO_COMANDO)
    estado = models.CharField(max_length=15, choices=ESTADO_COMANDO, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)
    ejecutado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'comando_remoto'
        verbose_name = 'Comando Remoto'
        verbose_name_plural = 'Comandos Remotos'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.tipo} → {self.dispositivo.nombre} [{self.estado}]"


# ─── RESPUESTA_COMANDO ────────────────────────────────────────────────────────
class RespuestaComando(models.Model):
    comando = models.OneToOneField(ComandoRemoto, on_delete=models.CASCADE, related_name='respuesta')
    exitoso = models.BooleanField(default=False)
    mensaje = models.TextField(blank=True)
    recibido_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'respuesta_comando'
        verbose_name = 'Respuesta de Comando'
        verbose_name_plural = 'Respuestas de Comandos'

    def __str__(self):
        estado = 'OK' if self.exitoso else 'FALLO'
        return f"{estado} | Comando {self.comando.id}"


# ─── ALERTA_SISTEMA ───────────────────────────────────────────────────────────
TIPO_ALERTA = [
    ('desconexion', 'Desconexión de dispositivo'),
    ('velocidad', 'Velocidad excesiva'),
    ('fuera_ruta', 'Vehículo fuera de ruta'),
    ('sin_gps', 'Sin señal GPS'),
    ('general', 'General'),
]

NIVEL_ALERTA = [
    ('info', 'Informativo'),
    ('advertencia', 'Advertencia'),
    ('critico', 'Crítico'),
]

class AlertaSistema(models.Model):
    dispositivo = models.ForeignKey(DispositivoIot, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertas')
    tipo = models.CharField(max_length=20, choices=TIPO_ALERTA, default='general')
    nivel = models.CharField(max_length=15, choices=NIVEL_ALERTA, default='info')
    mensaje = models.TextField()
    resuelta = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'alerta_sistema'
        verbose_name = 'Alerta del Sistema'
        verbose_name_plural = 'Alertas del Sistema'
        ordering = ['-creado_en']

    def __str__(self):
        return f"[{self.nivel.upper()}] {self.tipo} | {self.creado_en:%Y-%m-%d %H:%M}"


# ─── AUDITORIA_SISTEMA ────────────────────────────────────────────────────────
class AuditoriaSistema(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='auditorias')
    accion = models.CharField(max_length=100)
    tabla_afectada = models.CharField(max_length=50, blank=True)
    registro_id = models.IntegerField(null=True, blank=True)
    detalle = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_sistema'
        verbose_name = 'Auditoría del Sistema'
        verbose_name_plural = 'Auditorías del Sistema'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.usuario} | {self.accion} | {self.creado_en:%Y-%m-%d %H:%M}"


# ─── RECURSO (pantallas/módulos del sistema) ──────────────────────────────────
class Recurso(models.Model):
    nombre = models.CharField(max_length=100)
    ruta = models.CharField(max_length=100, help_text="Ruta Angular, ej: /dashboard")
    icono = models.CharField(max_length=50, blank=True, help_text="Nombre del icono")
    activo = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'recurso'
        verbose_name = 'Recurso'
        verbose_name_plural = 'Recursos'
        ordering = ['orden']

    def __str__(self):
        return self.nombre


# ─── ROL_RECURSO (permisos por rol) ───────────────────────────────────────────
class RolRecurso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='recursos')
    recurso = models.ForeignKey(Recurso, on_delete=models.CASCADE, related_name='roles')

    class Meta:
        db_table = 'rol_recurso'
        verbose_name = 'Rol Recurso'
        verbose_name_plural = 'Roles Recursos'
        unique_together = ('rol', 'recurso')

    def __str__(self):
        return f"{self.rol.nombre} → {self.recurso.nombre}"


# ─── PERFIL_USUARIO ───────────────────────────────────────────────────────────
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'perfil_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'

    def __str__(self):
        return f"{self.usuario.username} ({self.estado})"
