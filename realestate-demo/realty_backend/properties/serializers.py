from decimal import Decimal
from rest_framework import serializers
from .models import City, Property, NewsletterSubscriber, Inquiry
from .utils import format_price_label, format_rupee


class CitySerializer(serializers.ModelSerializer):
    listing_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'slug', 'image_url', 'listing_count']


class PropertyListSerializer(serializers.ModelSerializer):
    """Lean representation used for the listing grid — mirrors the fields
    the frontend's `listings` array cards actually render."""
    city = serializers.CharField(source='city.name', read_only=True)
    price_label = serializers.SerializerMethodField()
    tag = serializers.CharField(read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'city', 'address', 'price', 'price_label',
            'status', 'tag', 'property_type', 'bedrooms', 'bathrooms',
            'area_sqft', 'image_url', 'is_rera_verified',
        ]

    def get_price_label(self, obj):
        return format_price_label(obj.price, obj.status)


class PropertyDetailSerializer(PropertyListSerializer):
    """Full representation used for the property modal / single-property page."""

    class Meta(PropertyListSerializer.Meta):
        fields = PropertyListSerializer.Meta.fields + [
            'description', 'created_at', 'updated_at',
        ]


class PropertyWriteSerializer(serializers.ModelSerializer):
    """Used for creating/updating a listing (admin only)."""

    class Meta:
        model = Property
        fields = [
            'id', 'name', 'city', 'address', 'status', 'property_type',
            'price', 'bedrooms', 'bathrooms', 'area_sqft', 'image_url',
            'description', 'is_rera_verified', 'is_active',
        ]


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'city_interest', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at']


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ['id', 'property', 'name', 'email', 'phone', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


class EMICalculationRequestSerializer(serializers.Serializer):
    price = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=Decimal('0'))
    down_payment_percent = serializers.FloatField(min_value=0, max_value=100, default=20)
    interest_rate = serializers.FloatField(min_value=0, max_value=50, default=8.5)
    term_years = serializers.IntegerField(min_value=1, max_value=40, default=20)
