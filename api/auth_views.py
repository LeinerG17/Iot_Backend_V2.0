from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UsuarioRol, RolRecurso, PerfilUsuario


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Login personalizado que retorna tokens JWT + usuario + roles + recursos.
    El frontend Angular espera exactamente esta estructura.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': True, 'mensaje': 'Usuario y contraseña son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if not user:
        return Response(
            {'error': True, 'mensaje': 'Credenciales inválidas.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': True, 'mensaje': 'Usuario inactivo.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    # Obtener perfil
    try:
        perfil = user.perfil
        estado = perfil.estado
    except PerfilUsuario.DoesNotExist:
        estado = 'activo'

    # Obtener roles del usuario
    usuario_roles = UsuarioRol.objects.filter(usuario=user).select_related('rol')
    roles = [
        {'id': ur.rol.id, 'nombre': ur.rol.nombre}
        for ur in usuario_roles
    ]

    # Obtener recursos permitidos según los roles
    rol_ids = [ur.rol.id for ur in usuario_roles]
    rol_recursos = RolRecurso.objects.filter(
        rol_id__in=rol_ids, recurso__activo=True
    ).select_related('recurso').order_by('recurso__orden')

    # Eliminar duplicados manteniendo orden
    recursos_vistos = set()
    recursos = []
    for rr in rol_recursos:
        if rr.recurso.id not in recursos_vistos:
            recursos_vistos.add(rr.recurso.id)
            recursos.append({
                'id': rr.recurso.id,
                'nombre': rr.recurso.nombre,
                'ruta': rr.recurso.ruta,
                'icono': rr.recurso.icono,
            })

    # Si es superusuario, retornar todos los recursos
    if user.is_superuser:
        from .models import Recurso
        todos = Recurso.objects.filter(activo=True).order_by('orden')
        recursos = [
            {'id': r.id, 'nombre': r.nombre, 'ruta': r.ruta, 'icono': r.icono}
            for r in todos
        ]

    return Response({
        'access': access,
        'refresh': str(refresh),
        'usuario': {
            'idusuarios': user.id,
            'username': user.username,
            'email': user.email,
            'nombre': user.first_name,
            'apellido': user.last_name,
            'estado': estado,
        },
        'roles': roles,
        'recursos': recursos,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_view(request):
    """Registrar nuevo usuario"""
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    nombre = request.data.get('nombre', '')
    apellido = request.data.get('apellido', '')

    if not username or not password:
        return Response(
            {'error': True, 'mensaje': 'Usuario y contraseña son requeridos.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': True, 'mensaje': 'El nombre de usuario ya existe.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        first_name=nombre,
        last_name=apellido,
    )
    PerfilUsuario.objects.create(usuario=user)

    return Response(
        {'mensaje': f'Usuario {username} creado exitosamente.'},
        status=status.HTTP_201_CREATED
    )
