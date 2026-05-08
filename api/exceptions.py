from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        view = context.get('view', None)
        error_data = {
            'error': True,
            'codigo': response.status_code,
            'mensaje': _get_mensaje(response.status_code),
            'detalle': response.data,
        }
        if hasattr(view, '__class__'):
            error_data['endpoint'] = view.__class__.__name__

        logger.warning(f"API Error {response.status_code}: {response.data}")
        response.data = error_data

    return response


def _get_mensaje(status_code):
    mensajes = {
        400: 'Datos inválidos en la solicitud.',
        401: 'No autenticado. Proporciona un token JWT válido.',
        403: 'No tienes permisos para realizar esta acción.',
        404: 'El recurso solicitado no existe.',
        405: 'Método HTTP no permitido.',
        429: 'Demasiadas solicitudes. Intenta más tarde.',
        500: 'Error interno del servidor.',
    }
    return mensajes.get(status_code, 'Ocurrió un error inesperado.')
