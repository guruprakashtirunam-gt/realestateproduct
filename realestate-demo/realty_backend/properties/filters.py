import django_filters
from .models import Property


class PropertyFilter(django_filters.FilterSet):
    """Backs the homepage search bar (city, budget) and the
    All / For Sale / For Rent / New Launch filter buttons."""

    city = django_filters.CharFilter(field_name='city__name', lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    property_type = django_filters.CharFilter(field_name='property_type', lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_beds = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Property
        fields = ['city', 'status', 'property_type', 'min_price', 'max_price', 'min_beds']

    def filter_search(self, queryset, name, value):
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) | Q(address__icontains=value) | Q(city__name__icontains=value)
        )
