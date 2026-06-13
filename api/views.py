from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from math import radians, sin, cos, sqrt, atan2

from .models import (
    Rol, UsuarioRol, Conductor, Ruta, Parada, RutaParada,
    Vehiculo, DispositivoIot, AsignacionRuta, HorarioRuta,
    UbicacionGps, HistorialRecorrido, EstadoOperacion,
    ComandoRemoto, RespuestaComando, AlertaSistema, AuditoriaSistema
)
from .serializers import (
    RolSerializer, UsuarioRolSerializer, ConductorSerializer,
    RutaSerializer, ParadaSerializer, RutaParadaSerializer,
    VehiculoSerializer, DispositivoIotSerializer, AsignacionRutaSerializer,
    HorarioRutaSerializer, UbicacionGpsSerializer, HistorialRecorridoSerializer,
    EstadoOperacionSerializer, ComandoRemotoSerializer, RespuestaComandoSerializer,
    AlertaSistemaSerializer, AuditoriaSistemaSerializer,
    RutaDetalleSerializer, VehiculoUbicacionSerializer
)
from .filters import DispositivoFilter, UbicacionFilter, ComandoFilter, VehiculoFilter, AlertaFilter
from .pagination import StandardPagination


# ─── VIEWSETS CRUD completos ──────────────────────────────────────────────────

@extend_schema(tags=['roles'])
class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    pagination_class = StandardPagination


@extend_schema(tags=['usuarios'])
class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.select_related('usuario', 'rol').all()
    serializer_class = UsuarioRolSerializer
    pagination_class = StandardPagination


@extend_schema(tags=['conductores'])
class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all().order_by('nombre')
    serializer_class = ConductorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'cedula']
    pagination_class = StandardPagination


@extend_schema(tags=['rutas'])
class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all().order_by('nombre')
    serializer_class = RutaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']
    pagination_class = StandardPagination


@extend_schema(tags=['paradas'])
class ParadaViewSet(viewsets.ModelViewSet):
    queryset = Parada.objects.all()
    serializer_class = ParadaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']
    pagination_class = StandardPagination


@extend_schema(tags=['paradas'])
class RutaParadaViewSet(viewsets.ModelViewSet):
    queryset = RutaParada.objects.select_related('ruta', 'parada').all()
    serializer_class = RutaParadaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ruta']
    ordering_fields = ['orden']
    pagination_class = StandardPagination


@extend_schema(tags=['vehiculos'])
class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    filterset_class = VehiculoFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['placa', 'modelo']
    pagination_class = StandardPagination


@extend_schema(tags=['asignaciones'])
class AsignacionRutaViewSet(viewsets.ModelViewSet):
    queryset = AsignacionRuta.objects.select_related('conductor', 'vehiculo', 'ruta').all()
    serializer_class = AsignacionRutaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['activa', 'ruta', 'conductor', 'vehiculo']
    pagination_class = StandardPagination


@extend_schema(tags=['horarios'])
class HorarioRutaViewSet(viewsets.ModelViewSet):
    queryset = HorarioRuta.objects.select_related('ruta').all()
    serializer_class = HorarioRutaSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['ruta', 'dia_semana', 'activo']
    pagination_class = StandardPagination


@extend_schema(tags=['estados'])
class EstadoOperacionViewSet(viewsets.ModelViewSet):
    queryset = EstadoOperacion.objects.select_related('vehiculo').all()
    serializer_class = EstadoOperacionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['estado', 'vehiculo']
    pagination_class = StandardPagination


@extend_schema(tags=['respuestas'])
class RespuestaComandoViewSet(viewsets.ModelViewSet):
    queryset = RespuestaComando.objects.select_related('comando').all()
    serializer_class = RespuestaComandoSerializer
    pagination_class = StandardPagination


@extend_schema(tags=['auditorias'])
class AuditoriaSistemaViewSet(viewsets.ModelViewSet):
    queryset = AuditoriaSistema.objects.all()
    serializer_class = AuditoriaSistemaSerializer
    http_method_names = ['get']  # Solo lectura
    pagination_class = StandardPagination


# ─── DEVICES ──────────────────────────────────────────────────────────────────

@extend_schema(tags=['devices'], summary="Listar dispositivos IoT")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_devices(request):
    devices = DispositivoIot.objects.select_related('vehiculo').all()
    f = DispositivoFilter(request.GET, queryset=devices)
    paginator = StandardPagination()
    page = paginator.paginate_queryset(f.qs, request)
    return paginator.get_paginated_response(DispositivoIotSerializer(page, many=True).data)


@extend_schema(tags=['devices'], summary="Registrar dispositivo")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device(request):
    serializer = DispositivoIotSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'mensaje': 'Dispositivo registrado.', 'dispositivo': serializer.data}, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(tags=['devices'], summary="Detalle, actualizar o eliminar dispositivo")
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def device_detail(request, pk):
    try:
        device = DispositivoIot.objects.get(pk=pk)
    except DispositivoIot.DoesNotExist:
        return Response({'error': True, 'mensaje': 'Dispositivo no encontrado.'}, status=404)

    if request.method == 'GET':
        return Response(DispositivoIotSerializer(device).data)
    elif request.method == 'PUT':
        serializer = DispositivoIotSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'mensaje': 'Actualizado.', 'dispositivo': serializer.data})
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        device.delete()
        return Response({'mensaje': 'Dispositivo eliminado.'}, status=204)


# ─── READINGS ─────────────────────────────────────────────────────────────────

@extend_schema(tags=['readings'], summary="Recibir ubicación GPS del ESP32")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_reading(request):
    serializer = UbicacionGpsSerializer(data=request.data)
    if serializer.is_valid():
        reading = serializer.save()
        reading.dispositivo.ultima_conexion = timezone.now()
        reading.dispositivo.save(update_fields=['ultima_conexion'])
        return Response({'mensaje': 'Ubicación registrada.', 'lectura': serializer.data}, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(tags=['readings'], summary="Listar ubicaciones GPS")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_readings(request):
    readings = UbicacionGps.objects.select_related('dispositivo').all()
    f = UbicacionFilter(request.GET, queryset=readings)
    paginator = StandardPagination()
    page = paginator.paginate_queryset(f.qs, request)
    return paginator.get_paginated_response(UbicacionGpsSerializer(page, many=True).data)


# ─── COMMANDS ─────────────────────────────────────────────────────────────────

@extend_schema(tags=['commands'], summary="Enviar comando remoto (activar/desactivar)")
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_command(request):
    serializer = ComandoRemotoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'mensaje': 'Comando enviado.', 'comando': serializer.data}, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(tags=['commands'], summary="Listar comandos remotos")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_commands(request):
    commands = ComandoRemoto.objects.select_related('dispositivo').all()
    f = ComandoFilter(request.GET, queryset=commands)
    paginator = StandardPagination()
    page = paginator.paginate_queryset(f.qs, request)
    return paginator.get_paginated_response(ComandoRemotoSerializer(page, many=True).data)


@extend_schema(tags=['commands'], summary="Último comando pendiente para el ESP32")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_commands_latest(request):
    dispositivo_id = request.query_params.get('device')
    if not dispositivo_id:
        return Response({'error': True, 'mensaje': 'Parámetro requerido: ?device=<id>'}, status=400)

    command = ComandoRemoto.objects.filter(
        dispositivo_id=dispositivo_id, estado='pendiente'
    ).order_by('-creado_en').first()

    if command:
        command.estado = 'enviado'
        command.save(update_fields=['estado'])
        return Response({'comando': ComandoRemotoSerializer(command).data})

    return Response({'mensaje': 'Sin comandos pendientes.', 'comando': None})


# ─── ALERTAS ──────────────────────────────────────────────────────────────────

@extend_schema(tags=['alertas'], summary="Listar alertas del sistema")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_alertas(request):
    alertas = AlertaSistema.objects.all()
    f = AlertaFilter(request.GET, queryset=alertas)
    paginator = StandardPagination()
    page = paginator.paginate_queryset(f.qs, request)
    return paginator.get_paginated_response(AlertaSistemaSerializer(page, many=True).data)


# ─── ESPECIALES ───────────────────────────────────────────────────────────────

@extend_schema(tags=['ubicacion'], summary="Ubicación en tiempo real de todos los vehículos")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ubicacion_tiempo_real(request):
    vehiculos = Vehiculo.objects.filter(activo=True).prefetch_related('dispositivos')
    serializer = VehiculoUbicacionSerializer(vehiculos, many=True)
    return Response({'total_vehiculos': vehiculos.count(), 'vehiculos': serializer.data})


@extend_schema(tags=['rutas'], summary="Ruta con sus paradas ordenadas")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_con_paradas(request, pk):
    try:
        ruta = Ruta.objects.prefetch_related('ruta_paradas__parada').get(pk=pk)
    except Ruta.DoesNotExist:
        return Response({'error': True, 'mensaje': 'Ruta no encontrada.'}, status=404)
    return Response(RutaDetalleSerializer(ruta).data)


# ─── READING PÚBLICO para Arduino (sin JWT, usa identificador) ────────────────
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@api_view(['POST'])
@permission_classes([AllowAny])
def post_reading_public(request):
    identificador = request.data.get('identificador', '').strip().upper()
    if not identificador:
        return Response({'error': True, 'mensaje': 'Campo requerido: identificador'}, status=400)
    try:
        dispositivo = DispositivoIot.objects.get(identificador=identificador, activo=True)
    except DispositivoIot.DoesNotExist:
        return Response({'error': True, 'mensaje': 'Dispositivo no encontrado o inactivo'}, status=404)

    data = request.data.copy()
    data['dispositivo'] = dispositivo.id
    serializer = UbicacionGpsSerializer(data=data)
    if serializer.is_valid():
        lectura = serializer.save()
        dispositivo.ultima_conexion = timezone.now()
        dispositivo.save(update_fields=['ultima_conexion'])

        # ── Emitir por WebSocket ──────────────────────────────
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "ubicaciones",
            {
                "type": "ubicacion_update",
                "data": {
                    "dispositivo_id":   dispositivo.id,
                    "dispositivo_nombre": dispositivo.nombre,
                    "identificador":    dispositivo.identificador,
                    "latitud":          lectura.latitud,
                    "longitud":         lectura.longitud,
                    "velocidad":        lectura.velocidad,
                    "timestamp":        lectura.timestamp.isoformat(),
                    "vehiculo":         dispositivo.vehiculo.placa if dispositivo.vehiculo else None,
                }
            }
        )
        return Response({'mensaje': 'OK', 'lectura_id': lectura.id}, status=201)
    return Response(serializer.errors, status=400)

# ─── PARADA MÁS CERCANA (público) ─────────────────────────────────────────────
@extend_schema(tags=['ubicacion'], summary="Encontrar la parada más cercana a una ubicación")
@api_view(['GET'])
@permission_classes([AllowAny])
def parada_cercana(request):
    try:
        lat = float(request.query_params.get('lat', ''))
        lng = float(request.query_params.get('lng', ''))
    except (ValueError, TypeError):
        return Response({'error': True, 'mensaje': 'Parámetros requeridos: lat (float), lng (float)'}, status=400)
    paradas = Parada.objects.all()
    mejor = None
    min_dist = float('inf')
    R = 6371
    for p in paradas:
        dlat = radians(p.latitud - lat)
        dlon = radians(p.longitud - lng)
        a = sin(dlat/2)**2 + cos(radians(lat)) * cos(radians(p.latitud)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        dist = R * c
        if dist < min_dist:
            min_dist = dist
            mejor = p
    if not mejor:
        return Response({'mensaje': 'No hay paradas registradas.'}, status=404)
    rutas = Ruta.objects.filter(ruta_paradas__parada=mejor, activa=True).distinct()
    return Response({
        'parada': {
            'id': mejor.id, 'nombre': mejor.nombre,
            'latitud': mejor.latitud, 'longitud': mejor.longitud,
            'descripcion': mejor.descripcion,
        },
        'distancia_km': round(min_dist, 3),
        'distancia_m': round(min_dist * 1000, 1),
        'rutas': [{'id': r.id, 'nombre': r.nombre} for r in rutas],
    })


# ─── DISPOSITIVOS ACTIVOS (admin) ──────────────────────────────────────────────
@extend_schema(tags=['devices'], summary="Listar dispositivos con estado de conexión")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dispositivos_activos(request):
    dispositivos = DispositivoIot.objects.select_related('vehiculo').all()
    resultado = []
    for d in dispositivos:
        ultima = UbicacionGps.objects.filter(dispositivo=d).order_by('-timestamp').first()
        resultado.append({
            'id': d.id, 'nombre': d.nombre, 'tipo': d.tipo,
            'identificador': d.identificador, 'activo': d.activo,
            'ultima_conexion': d.ultima_conexion,
            'vehiculo_placa': d.vehiculo.placa if d.vehiculo else None,
            'estado_conexion': DispositivoIotSerializer().get_estado_conexion(d),
            'ultima_ubicacion': {
                'latitud': ultima.latitud, 'longitud': ultima.longitud,
                'velocidad_kmh': ultima.velocidad, 'timestamp': ultima.timestamp,
            } if ultima else None,
        })
    return Response({'dispositivos': resultado})


# ─── COORDENADAS DE RUTA PARA OSRM ────────────────────────────────────────────
@extend_schema(tags=['rutas'], summary="Coordenadas ordenadas de una ruta para trazar recorrido")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_coordenadas(request, pk):
    try:
        ruta = Ruta.objects.prefetch_related('ruta_paradas__parada').get(pk=pk)
    except Ruta.DoesNotExist:
        return Response({'error': True, 'mensaje': 'Ruta no encontrada.'}, status=404)
    paradas = ruta.ruta_paradas.select_related('parada').order_by('orden')
    coords = [{'lat': rp.parada.latitud, 'lng': rp.parada.longitud, 'nombre': rp.parada.nombre, 'orden': rp.orden} for rp in paradas]
    return Response({'id': ruta.id, 'nombre': ruta.nombre, 'paradas': coords})


# ─── USUARIOS ─────────────────────────────────────────────────────────────────
from django.contrib.auth.models import User
from .serializers import (UsuarioSerializer, UsuarioCreateSerializer,
                           RecursoSerializer, RolRecursoSerializer, PerfilUsuarioSerializer)
from .models import Recurso, RolRecurso, PerfilUsuario

@extend_schema(tags=['usuarios'])
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('username')
    pagination_class = StandardPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer


@extend_schema(tags=['recursos'])
class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recurso.objects.all().order_by('orden')
    serializer_class = RecursoSerializer
    pagination_class = StandardPagination


@extend_schema(tags=['rol-recurso'])
class RolRecursoViewSet(viewsets.ModelViewSet):
    queryset = RolRecurso.objects.select_related('rol', 'recurso').all()
    serializer_class = RolRecursoSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rol', 'recurso']


@extend_schema(tags=['perfiles'])
class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.select_related('usuario').all()
    serializer_class = PerfilUsuarioSerializer
    pagination_class = StandardPagination


# ─── ENDPOINT ESTUDIANTE ──────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rutas_estudiante(request):
    from .models import Ruta, AsignacionRuta

    rutas = Ruta.objects.filter(activa=True).prefetch_related('ruta_paradas__parada')
    resultado = []

    for ruta in rutas:
        ruta_paradas = ruta.ruta_paradas.select_related('parada').order_by('orden')
        paradas = [{
            'id': rp.parada.id,
            'nombre': rp.parada.nombre,
            'latitud': rp.parada.latitud,
            'longitud': rp.parada.longitud,
            'descripcion': rp.parada.descripcion,
            'orden': rp.orden,
        } for rp in ruta_paradas]

        asignacion = AsignacionRuta.objects.filter(
            ruta=ruta, activa=True
        ).select_related('conductor', 'vehiculo').first()

        conductor = None
        vehiculo_id = None
        if asignacion and asignacion.conductor:
            conductor = {
                'nombre': asignacion.conductor.nombre,
                'telefono': asignacion.conductor.telefono,
                'vehiculo': asignacion.vehiculo.placa if asignacion.vehiculo else '',
            }
            vehiculo_id = asignacion.vehiculo.id if asignacion.vehiculo else None

        dispositivos_online = []
        if vehiculo_id:
            dispositivos = DispositivoIot.objects.filter(vehiculo_id=vehiculo_id, activo=True)
            for d in dispositivos:
                if d.ultima_conexion and (timezone.now() - d.ultima_conexion).total_seconds() < 300:
                    dispositivos_online.append(d.nombre)

        resultado.append({
            'id': ruta.id,
            'nombre': ruta.nombre,
            'descripcion': ruta.descripcion,
            'activa': ruta.activa,
            'total_paradas': len(paradas),
            'paradas': paradas,
            'conductor': conductor,
            'operativa': len(dispositivos_online) > 0,
            'dispositivos_online': dispositivos_online,
        })

    return Response({'rutas': resultado})