from django.contrib import admin
from .models import City, Property, NewsletterSubscriber, Inquiry


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'listing_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def listing_count(self, obj):
        return obj.get_listing_count()


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'status', 'property_type', 'price', 'is_active', 'created_at']
    list_filter = ['status', 'property_type', 'city', 'is_active', 'is_rera_verified']
    search_fields = ['name', 'address']
    autocomplete_fields = ['city']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'city_interest', 'subscribed_at', 'is_active']
    search_fields = ['email']


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'property', 'created_at', 'is_resolved']
    list_filter = ['is_resolved']
    search_fields = ['name', 'email']
