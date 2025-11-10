from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

# Make Destination model with fields for country. It will include different tourist attractions within a country


from django.db import models

class Continent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True)  # e.g., 'AF' for Africa

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Continents"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)  # ISO 3-letter code, e.g., 'USA'
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name='countries')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']



class AdventureStyle(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., 'Hiking', 'Safari', 'Cultural Tour'
    description = models.TextField(max_length=500, blank=True, null=True)  # Optional description
    # icon = models.ImageField(upload_to='adventure_styles/', blank=True, null=True)  # Optional icon/image
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Adventure Styles"
        ordering = ['name']


class Destination(models.Model):
    name = models.CharField(max_length=255)  # e.g., 'Eiffel Tower', 'Serengeti National Park'
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='destinations')
    city = models.CharField(max_length=255, help_text="Type the primary city for this destination.")  # NEW: Singular CharField, user types
    description = models.TextField(max_length=500, blank=True, null=True)  # Optional details about the attraction

    # Add more fields like latitude/longitude, category (e.g., 'Historical', 'Natural') if needed later

    def __str__(self):
        return f"{self.name} ({self.country.name})"

    class Meta:
        verbose_name_plural = "Destinations"
        ordering = ['name']




class TournTrips(models.Model):
    # Traveler details
    title = models.CharField(max_length=255)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='tours')  # Changed to ForeignKey for dropdown in admin
    duration = models.CharField(max_length=32)
    # NEW fields – only used in the admin form
    _days   = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Days",
        help_text="Number of days (0 if unknown)",
    )
    _nights = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Nights",
        help_text="Number of nights (0 if unknown)",
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, f"{i} Star") for i in range(1, 6)],
        help_text="Preferred hotel star rating",
    )
    no_of_reviews = models.PositiveIntegerField(default=0)
    destinations = models.ManyToManyField(Destination, related_name='tours')  # Changed to ManyToMany for multi-select in admin
    shadow_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    departure_date = models.DateField()
    adventure_styles = models.ForeignKey(AdventureStyle, on_delete=models.PROTECT, related_name='tours')  # Changed to ForeignKey for dropdown in admin
    start_city = models.CharField(max_length=255)
    end_city = models.CharField(max_length=255)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Tour Trips"

    # ------------------------------------------------------------------
    # Helper property – automatically builds the string for the old field
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        # Build the string **before** we call super().save()
        if self._days or self._nights:
            self.duration = f"{self._nights} nights {self._days} days"
        else:
            self.duration = ""
        super().save(*args, **kwargs)

    # Optional: nice display in admin list / detail
    @property
    def duration_display(self):
        return self.duration or "—"

    # ------------------------------------------------------------------
    # US-format departure date (used in admin list)
    # ------------------------------------------------------------------
    @property
    def departure_date_us(self):
        return self.departure_date.strftime("%m/%d/%Y")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Tour Trips"