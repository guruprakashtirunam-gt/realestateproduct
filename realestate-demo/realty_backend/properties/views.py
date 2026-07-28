from django.db.models import Count, Q
import django_filters.rest_framework
from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import City, Property, NewsletterSubscriber, Inquiry
from .serializers import (
    CitySerializer, PropertyListSerializer, PropertyDetailSerializer,
    PropertyWriteSerializer, NewsletterSubscriberSerializer, InquirySerializer,
    EMICalculationRequestSerializer,
)
from .filters import PropertyFilter


class IsAdminOrReadOnly(permissions.BasePermission):
    """Anyone can browse listings; only staff/admin accounts can create,
    edit, or delete them (matches: content is managed by the agency, not
    site visitors)."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/cities/  — powers the 'Search by city' grid, including a
    live listing_count per city instead of the hardcoded numbers in the
    original frontend mock data."""
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return City.objects.annotate(
            listing_count=Count('properties', filter=Q(properties__is_active=True))
        ).order_by('-listing_count')


class PropertyViewSet(viewsets.ModelViewSet):
    """
    GET    /api/properties/           list + filter + search (see PropertyFilter)
    GET    /api/properties/{id}/      single listing detail (feeds the modal)
    POST   /api/properties/           create a listing (staff only)
    PUT    /api/properties/{id}/      update a listing (staff only)
    PATCH  /api/properties/{id}/      partial update (staff only)
    DELETE /api/properties/{id}/      remove a listing (staff only)

    Query params:
      ?city=Mumbai
      ?status=sale|rent|new           (matches the filter buttons)
      ?property_type=Apartment
      ?min_price=1000000&max_price=5000000
      ?min_beds=2
      ?search=bandra                  (matches name / address / city)
      ?ordering=price | -price | created_at | -created_at
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = PropertyFilter
    ordering_fields = ['price', 'created_at', 'area_sqft']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Property.objects.select_related('city')
        if self.request.method in permissions.SAFE_METHODS:
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return PropertyWriteSerializer
        if self.action == 'retrieve':
            return PropertyDetailSerializer
        return PropertyListSerializer


class NewsletterSubscribeView(APIView):
    """POST /api/newsletter/subscribe/  — backs the '#newsletter-form' email
    capture at the bottom of the homepage."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'city_interest_id': request.data.get('city_interest')},
        )
        if not created and not subscriber.is_active:
            subscriber.is_active = True
            subscriber.save(update_fields=['is_active'])

        message = (
            "You're on the list — first listing lands next week."
            if created else "You're already subscribed — we'll keep the emails coming."
        )
        serializer = NewsletterSubscriberSerializer(subscriber)
        return Response(
            {'message': message, 'subscriber': serializer.data},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class InquiryCreateView(APIView):
    """POST /api/inquiries/  — 'Contact us about this property' lead capture.
    (Extends the frontend with a backend-supported feature; wire it up to a
    small form in the property modal if you'd like visitors to request a call
    back about a specific listing.)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = InquirySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {'message': "Thanks — an agent will reach out shortly.", 'inquiry': serializer.data},
            status=status.HTTP_201_CREATED,
        )


class EMICalculatorView(APIView):
    """POST /api/emi/calculate/ — server-side mirror of the frontend's
    calcEMI() so the same numbers can be trusted/reused elsewhere (e.g. in a
    saved-quote email, or a mobile client that isn't running the JS)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EMICalculationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        price = float(data['price'])
        down_pct = data['down_payment_percent']
        rate = data['interest_rate']
        term_years = data['term_years']

        down_amount = price * down_pct / 100
        loan = price - down_amount
        r = (rate / 100) / 12
        n = term_years * 12

        if r == 0:
            emi = loan / n
        else:
            emi = loan * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

        total_paid = emi * n
        total_interest = total_paid - loan

        return Response({
            'monthly_emi': round(emi, 2),
            'loan_amount': round(loan, 2),
            'down_payment_amount': round(down_amount, 2),
            'total_interest': round(total_interest, 2),
            'total_payable': round(total_paid + down_amount, 2),
        })
