from rest_framework import serializers
from django.utils import timezone
from .models import (
    Rol, UsuarioRol, Conductor, Ruta, Parada, RutaParada,
    Vehiculo, DispositivoIot, AsignacionRuta, HorarioRuta,
    UbicacionGps, HistorialRecorrido, EstadoOperacion,
    ComandoRemoto, RespuestaComando, AlertaSistema, AuditoriaSistema
)


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioRolSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsuarioRol
        fields = '__all__'


class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = '__all__'

    def validate_cedula(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("La cédula debe contener solo números.")
        return value


class RutaSerializer(serializers.ModelSerializer):
    total_paradas = serializers.SerializerMethodField()

    class Meta:
        model = Ruta
        fields = '__all__'

    def get_total_paradas(self, obj):
        return obj.ruta_paradas.count()


class ParadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parada
        fields = '__all__'

    def validate_latitud(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitud debe estar entre -90 y 90.")
        return value

    def validate_longitud(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitud debe estar entre -180 y 180.")
        return value


class RutaParadaSerializer(serializers.ModelSerializer):
    parada_nombre = serializers.CharField(source='parada.nombre', read_only=True)
    parada_latitud = serializers.FloatField(source='parada.latitud', read_only=True)
    parada_longitud = serializers.FloatField(source='parada.longitud', read_only=True)

    class Meta:
        model = RutaParada
        fields = '__all__'


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'

    def validate_placa(self, value):
        return value.upper()

    def validate_capacidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a 0.")
        return value


class DispositivoIotSerializer(serializers.ModelSerializer):
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)
    estado_conexion = serializers.SerializerMethodField()

    class Meta:
        model = DispositivoIot
        fields = '__all__'

    def get_estado_conexion(self, obj):
        if not obj.ultima_conexion:
            return 'nunca_conectado'
        diff = timezone.now() - obj.ultima_conexion
        if diff.total_seconds() < 60:
            return 'en_linea'
        elif diff.total_seconds() < 300:
            return 'reciente'
        return 'desconectado'

    def validate_identificador(self, value):
        return value.upper()


class AsignacionRutaSerializer(serializers.ModelSerializer):
    conductor_nombre = serializers.CharField(source='conductor.nombre', read_only=True)
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)
    ruta_nombre = serializers.CharField(source='ruta.nombre', read_only=True)

    class Meta:
        model = AsignacionRuta
        fields = '__all__'


class HorarioRutaSerializer(serializers.ModelSerializer):
    ruta_nombre = serializers.CharField(source='ruta.nombre', read_only=True)

    class Meta:
        model = HorarioRuta
        fields = '__all__'


class UbicacionGpsSerializer(serializers.ModelSerializer):
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)

    class Meta:
        model = UbicacionGps
        fields = '__all__'

    def validate_latitud(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitud inválida.")
        return value

    def validate_longitud(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitud inválida.")
        return value

    def validate_velocidad(self, value):
        if value < 0 or value > 200:
            raise serializers.ValidationError("Velocidad fuera de rango (0-200 km/h).")
        return value

    def validate(self, data):
        dispositivo = data.get('dispositivo')
        if dispositivo and not dispositivo.activo:
            raise serializers.ValidationError({"dispositivo": "El dispositivo está inactivo."})
        return data


class HistorialRecorridoSerializer(serializers.ModelSerializer):
    duracion_minutos = serializers.SerializerMethodField()

    class Meta:
        model = HistorialRecorrido
        fields = '__all__'

    def get_duracion_minutos(self, obj):
        if obj.fin:
            return round((obj.fin - obj.inicio).total_seconds() / 60, 1)
        return None


class EstadoOperacionSerializer(serializers.ModelSerializer):
    vehiculo_placa = serializers.CharField(source='vehiculo.placa', read_only=True)

    class Meta:
        model = EstadoOperacion
        fields = '__all__'


class ComandoRemotoSerializer(serializers.ModelSerializer):
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)

    class Meta:
        model = ComandoRemoto
        fields = '__all__'

    def validate(self, data):
        dispositivo = data.get('dispositivo')
        if dispositivo and not dispositivo.activo:
            raise serializers.ValidationError({"dispositivo": "No se pueden enviar comandos a un dispositivo inactivo."})
        return data


class RespuestaComandoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaComando
        fields = '__all__'


class AlertaSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaSistema
        fields = '__all__'


class AuditoriaSistemaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = AuditoriaSistema
        fields = '__all__'


# ─── ENRIQUECIDOS ──────────────────────────────────────────────────────────────
class RutaDetalleSerializer(serializers.ModelSerializer):
    paradas = RutaParadaSerializer(source='ruta_paradas', many=True, read_only=True)

    class Meta:
        model = Ruta
        fields = '__all__'


class VehiculoUbicacionSerializer(serializers.ModelSerializer):
    ultima_ubicacion = serializers.SerializerMethodField()
    estado_dispositivo = serializers.SerializerMethodField()

    class Meta:
        model = Vehiculo
        fields = '__all__'

    def get_ultima_ubicacion(self, obj):
        reading = UbicacionGps.objects.filter(
            dispositivo__vehiculo=obj
        ).order_by('-timestamp').first()
        if reading:
            return {
                'latitud': reading.latitud,
                'longitud': reading.longitud,
                'velocidad_kmh': reading.velocidad,
                'timestamp': reading.timestamp,
            }
        return None

    def get_estado_dispositivo(self, obj):
        dispositivo = obj.dispositivos.filter(activo=True).first()
        if not dispositivo:
            return 'sin_dispositivo'
        if not dispositivo.ultima_conexion:
            return 'nunca_conectado'
        diff = timezone.now() - dispositivo.ultima_conexion
        if diff.total_seconds() < 60:
            return 'en_linea'
        elif diff.total_seconds() < 300:
            return 'reciente'
        return 'desconectado'


# ─── NUEVOS SERIALIZERS PARA EL FRONTEND ─────────────────────────────────────
from django.contrib.auth.models import User
from .models import Recurso, RolRecurso, PerfilUsuario


class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recurso
        fields = '__all__'


class RolRecursoSerializer(serializers.ModelSerializer):
    recurso_nombre = serializers.CharField(source='recurso.nombre', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = RolRecurso
        fields = '__all__'


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    estado = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'date_joined', 'estado', 'roles']

    def get_estado(self, obj):
        try:
            return obj.perfil.estado
        except Exception:
            return 'activo'

    def get_roles(self, obj):
        return [ur.rol.nombre for ur in obj.roles.select_related('rol').all()]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        PerfilUsuario.objects.create(usuario=user)
        return user
