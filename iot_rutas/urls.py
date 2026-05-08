from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from api.auth_views import login_view, registro_view
from api.student_views import registro_estudiante, login_estudiante, rutas_estudiante, ruta_detalle_estudiante

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth admin
    path('api/auth/login/',    login_view,                 name='login'),
    path('api/auth/registro/', registro_view,              name='registro'),
    path('api/auth/refresh/',  TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/verify/',   TokenVerifyView.as_view(),  name='token_verify'),

    # Auth + rutas Estudiante
    path('api/estudiante/registro/',       registro_estudiante,       name='registro_estudiante'),
    path('api/estudiante/login/',          login_estudiante,          name='login_estudiante'),
    path('api/estudiante/rutas/',          rutas_estudiante,          name='rutas_estudiante'),
    path('api/estudiante/rutas/<int:pk>/', ruta_detalle_estudiante,   name='ruta_detalle_estudiante'),

    # API principal
    path('api/', include('api.urls')),

    # Documentación
    path('api/schema/', SpectacularAPIView.as_view(),                      name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',  SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),

    # React SPA (debe ir al final)
    #re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name='index.html'), name='react'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
