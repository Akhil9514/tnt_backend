# models.py
import re
from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from toursntrips.models import TournTrips

phone_regex = RegexValidator(
    regex=r"^\+?1?\d{9,15}$",
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

class TravellerCount(models.Model):
    """
    Stores breakdown of travellers. Belongs to one Traveller.
    """
    traveller = models.OneToOneField(
        'Traveller',
        on_delete=models.CASCADE,
        related_name='count',  # ← Clean reverse name
        help_text=_("The booking this count belongs to")
    )
    adults = models.PositiveSmallIntegerField(
        default=1,
        help_text=_("Number of adults (≥ 18 years)")
    )
    children = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Number of children (2–17 years)")
    )
    infants = models.PositiveSmallIntegerField(
        default=0,
        help_text=_("Number of infants (0–2 years)")
    )

    class Meta:
        verbose_name = _("Traveller breakdown")
        verbose_name_plural = _("Traveller breakdowns")

    def __str__(self):
        parts = []
        if self.adults:
            parts.append(f"{self.adults} adult{'' if self.adults == 1 else 's'}")
        if self.children:
            parts.append(f"{self.children} child{'' if self.children == 1 else 'ren'}")
        if self.infants:
            parts.append(f"{self.infants} infant{'' if self.infants == 1 else 's'}")
        return ", ".join(parts) or "—"


class Traveller(models.Model):
    name = models.CharField(max_length=255, help_text=_("Full name of the lead traveller"))
    phone_number = models.CharField(validators=[phone_regex], max_length=17, help_text=_("e.g. +12025550123"))
    email = models.EmailField(help_text=_("Contact email address"))
    nationality = models.CharField(max_length=100, help_text=_("Country of citizenship"))
    check_in_date = models.DateField(help_text=_("Arrival / check-in date"))
    check_out_date = models.DateField(help_text=_("Departure / check-out date"))
    # REMOVE THIS LINE ENTIRELY:
    # traveller_count = models.OneToOneField(TravellerCount, ...)
    HOTEL_RATING_CHOICES = [(i, f"{i} Star") for i in range(1, 6)]
    hotel_rating = models.PositiveSmallIntegerField(
        choices=HOTEL_RATING_CHOICES,
        help_text=_("Preferred hotel star rating")
    )
    is_direct_flight = models.BooleanField(
        default=False,
        help_text=_("Check if a direct (non-stop) flight is required")
    )

    class Meta:
        verbose_name = _("Traveller")
        verbose_name_plural = _("Travellers")
        ordering = ["-check_in_date"]

    def __str__(self):
        return f"{self.name} – {self.check_in_date} to {self.check_out_date}"

    @property
    def nights(self):
        return (self.check_out_date - self.check_in_date).days


class Visiting(models.Model):
    """
    Represents a Traveller booking a specific Tour Trip.
    """
    request_country = models.CharField(max_length=255, help_text=_("Country of origin"))
    traveller = models.ForeignKey(
        'Traveller',
        on_delete=models.CASCADE,
        related_name='visits',  # traveller.visits.all()
        help_text=_("The lead traveller for this booking")
    )
    tour = models.ForeignKey(
        TournTrips,
        on_delete=models.PROTECT,
        related_name='visitors',  # tour.visitors.all()
        help_text=_("The tour package being booked")
    )
    booked_on = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When this booking was created")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Any special requests or notes")
    )

    class Meta:
        verbose_name = _("Visiting / Booking")
        verbose_name_plural = _("Visitings / Bookings")
        unique_together = ('traveller', 'tour')  # one booking per tour per traveller
        ordering = ['-booked_on']

    def __str__(self):
        return f"{self.traveller.name} → {self.tour.title}"

    # ------------------------------------------------------------------
    # US-formatted dates for admin & templates
    # ------------------------------------------------------------------
    @property
    def tour_departure_us(self):
        return self.tour.departure_date.strftime('%m/%d/%Y')

    @property
    def traveller_check_in_us(self):
        return self.traveller.check_in_date.strftime('%m/%d/%Y')

    @property
    def traveller_check_out_us(self):
        return self.traveller.check_out_date.strftime('%m/%d/%Y')

