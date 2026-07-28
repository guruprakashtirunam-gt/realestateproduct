from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class City(models.Model):
    """A city shown in the 'Search by city' grid on the homepage."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name

    def get_listing_count(self):
        """Use this in places (like the admin) that don't already annotate
        `listing_count` on the queryset via CityViewSet.get_queryset()."""
        return self.properties.filter(is_active=True).count()


class Property(models.Model):
    """A single property listing (matches the `listings` array in the frontend)."""

    class Status(models.TextChoices):
        SALE = 'sale', 'For Sale'
        RENT = 'rent', 'For Rent'
        NEW = 'new', 'New Launch'

    class PropertyType(models.TextChoices):
        APARTMENT = 'Apartment', 'Apartment'
        VILLA = 'Villa', 'Villa'
        PENTHOUSE = 'Penthouse', 'Penthouse'
        INDEPENDENT_HOUSE = 'Independent House', 'Independent House'
        PLOT = 'Plot', 'Plot'
        STUDIO = 'Studio', 'Studio'

    name = models.CharField(max_length=200)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='properties')
    address = models.CharField(max_length=255, help_text="e.g. 'Bandra West, Mumbai'")

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.SALE)
    property_type = models.CharField(max_length=30, choices=PropertyType.choices, default=PropertyType.APARTMENT)

    # Stored in rupees. For 'rent' listings this is the monthly rent.
    price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])

    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    area_sqft = models.PositiveIntegerField(help_text="Carpet/built-up area in square feet")

    image_url = models.URLField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    is_rera_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text="Unpublish instead of deleting")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'properties'

    def __str__(self):
        return f"{self.name} ({self.city.name})"

    @property
    def tag(self):
        """Matches the 'For Sale' / 'For Rent' / 'New Launch' badge on the card."""
        return self.Status(self.status).label


class NewsletterSubscriber(models.Model):
    """Backs the 'Get new listings in your city' email capture form."""
    email = models.EmailField(unique=True)
    city_interest = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, blank=True, related_name='newsletter_subscribers'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email


class Inquiry(models.Model):
    """A lead captured when a visitor asks to be contacted about a specific property."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'inquiries'

    def __str__(self):
        return f"Inquiry from {self.name} about {self.property.name}"
