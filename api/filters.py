import django_filters
from .models import DispositivoIot, UbicacionGps, ComandoRemoto, Vehiculo, Parada, HistorialRecorrido, AlertaSistema


class DispositivoFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter(lookup_expr='iexact')
    activo = django_filters.BooleanFilter()
    vehiculo = django_filters.NumberFilter(field_name='vehiculo__id')

    class Meta:
        model = DispositivoIot
        fields = ['tipo', 'activo', 'vehiculo']


class UbicacionFilter(django_filters.FilterSet):
    dispositivo = django_filters.NumberFilter(field_name='dispositivo__id')
    desde = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    hasta = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')
    velocidad_min = django_filters.NumberFilter(field_name='velocidad', lookup_expr='gte')
    velocidad_max = django_filters.NumberFilter(field_name='velocidad', lookup_expr='lte')

    class Meta:
        model = UbicacionGps
        fields = ['dispositivo', 'desde', 'hasta', 'velocidad_min', 'velocidad_max']


class ComandoFilter(django_filters.FilterSet):
    dispositivo = django_filters.NumberFilter(field_name='dispositivo__id')
    estado = django_filters.CharFilter(lookup_expr='iexact')
    tipo = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = ComandoRemoto
        fields = ['dispositivo', 'estado', 'tipo']


class VehiculoFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter()

    class Meta:
        model = Vehiculo
        fields = ['activo']


class ParadaFilter(django_filters.FilterSet):
    ruta = django_filters.NumberFilter(field_name='ruta_paradas__ruta__id')

    class Meta:
        model = Parada
        fields = ['ruta']


class RecorridoFilter(django_filters.FilterSet):
    activo = django_filters.BooleanFilter()

    class Meta:
        model = HistorialRecorrido
        fields = ['activo']


class AlertaFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter(lookup_expr='iexact')
    nivel = django_filters.CharFilter(lookup_expr='iexact')
    resuelta = django_filters.BooleanFilter()

    class Meta:
        model = AlertaSistema
        fields = ['tipo', 'nivel', 'resuelta']
