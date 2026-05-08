from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Ruta, PerfilUsuario, Rol, UsuarioRol


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_estudiante(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    email    = request.data.get('email', '').strip()
    nombre   = request.data.get('nombre', '').strip()
    apellido = request.data.get('apellido', '').strip()

    if not username or not password:
        return Response({'error': True, 'mensaje': 'Usuario y contraseña son requeridos.'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': True, 'mensaje': 'El nombre de usuario ya existe.'}, status=400)

    user = User.objects.create_user(username=username, password=password, email=email, first_name=nombre, last_name=apellido)
    PerfilUsuario.objects.get_or_create(usuario=user)

    rol, _ = Rol.objects.get_or_create(nombre='Estudiante', defaults={'descripcion': 'Acceso de solo lectura a rutas y mapa'})
    UsuarioRol.objects.get_or_create(usuario=user, rol=rol)

    return Response({'mensaje': f'Estudiante {username} registrado correctamente.'}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_estudiante(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    if not username or not password:
        return Response({'error': True, 'mensaje': 'Usuario y contraseña son requeridos.'}, status=400)

    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': True, 'mensaje': 'Credenciales inválidas.'}, status=401)
    if not user.is_active:
        return Response({'error': True, 'mensaje': 'Usuario inactivo.'}, status=401)

    es_estudiante = user.is_superuser or user.roles.filter(rol__nombre='Estudiante').exists()
    if not es_estudiante:
        return Response({'error': True, 'mensaje': 'Esta cuenta no tiene acceso al portal de estudiantes.'}, status=403)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'usuario': {'id': user.id, 'username': user.username, 'nombre': user.first_name, 'apellido': user.last_name, 'email': user.email, 'rol': 'Estudiante'},
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def rutas_estudiante(request):
    rutas = Ruta.objects.filter(activa=True).prefetch_related('ruta_paradas__parada', 'asignaciones__conductor')
    resultado = []
    for ruta in rutas:
        asignacion = ruta.asignaciones.filter(activa=True).select_related('conductor').first()
        conductor = None
        if asignacion:
            c = asignacion.conductor
            conductor = {'nombre': c.nombre, 'telefono': c.telefono or None}

        paradas = [
            {'orden': rp.orden, 'nombre': rp.parada.nombre, 'latitud': rp.parada.latitud, 'longitud': rp.parada.longitud, 'descripcion': rp.parada.descripcion or None}
            for rp in ruta.ruta_paradas.all().order_by('orden')
        ]
        resultado.append({'id': ruta.id, 'nombre': ruta.nombre, 'descripcion': ruta.descripcion or None, 'conductor': conductor, 'paradas': paradas, 'total_paradas': len(paradas)})

    return Response({'rutas': resultado, 'total': len(resultado)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ruta_detalle_estudiante(request, pk):
    try:
        ruta = Ruta.objects.prefetch_related('ruta_paradas__parada', 'asignaciones__conductor').get(pk=pk, activa=True)
    except Ruta.DoesNotExist:
        return Response({'error': True, 'mensaje': 'Ruta no encontrada.'}, status=404)

    asignacion = ruta.asignaciones.filter(activa=True).select_related('conductor').first()
    conductor = None
    if asignacion:
        c = asignacion.conductor
        conductor = {'nombre': c.nombre, 'telefono': c.telefono or None}

    paradas = [
        {'orden': rp.orden, 'nombre': rp.parada.nombre, 'latitud': rp.parada.latitud, 'longitud': rp.parada.longitud, 'descripcion': rp.parada.descripcion or None}
        for rp in ruta.ruta_paradas.all().order_by('orden')
    ]
    return Response({'id': ruta.id, 'nombre': ruta.nombre, 'descripcion': ruta.descripcion or None, 'conductor': conductor, 'paradas': paradas, 'total_paradas': len(paradas)})
