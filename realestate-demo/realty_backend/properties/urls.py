from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    CityViewSet, PropertyViewSet, NewsletterSubscribeView,
    InquiryCreateView, EMICalculatorView,
)

router = DefaultRouter()
router.register('properties', PropertyViewSet, basename='property')
router.register('cities', CityViewSet, basename='city')

urlpatterns = [
    path('', include(router.urls)),
    path('newsletter/subscribe/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('inquiries/', InquiryCreateView.as_view(), name='inquiry-create'),
    path('emi/calculate/', EMICalculatorView.as_view(), name='emi-calculate'),
    # POST {"username": "...", "password": "..."} -> {"token": "..."}
    # Use this token as `Authorization: Token <token>` to create/edit/delete properties.
    path('auth/token/', obtain_auth_token, name='api-token-auth'),
]
