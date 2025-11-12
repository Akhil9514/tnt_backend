# bookings/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Traveller, TravellerCount, Visiting, ContactMessage


# ------------------------------------------------------------------
# Inline: Show TravellerCount inside Traveller
# ------------------------------------------------------------------
class TravellerCountInline(admin.StackedInline):
    model = TravellerCount
    fk_name = 'traveller'
    extra = 0
    max_num = 1
    fields = ('adults', 'children', 'infants')


# ------------------------------------------------------------------
# Inline: Show Visits inside Traveller
# ------------------------------------------------------------------
class VisitingInline(admin.TabularInline):
    model = Visiting
    extra = 0
    fields = ('tour', 'tour_departure_us', 'booked_on')
    readonly_fields = ('tour_departure_us', 'booked_on')

    def tour_departure_us(self, obj):
        return obj.tour_departure_us
    tour_departure_us.short_description = "Tour Departure"


# ------------------------------------------------------------------
# Traveller Admin
# ------------------------------------------------------------------
@admin.register(Traveller)
class TravellerAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'nationality',
        'check_in_us', 'check_out_us',
        'nights_display', 'traveller_breakdown',
        'hotel_rating_stars', 'is_direct_flight'
    )
    list_filter = ('nationality', 'hotel_rating', 'is_direct_flight', 'check_in_date')
    search_fields = ('name', 'email', 'phone_number', 'nationality')
    date_hierarchy = 'check_in_date'
    inlines = [TravellerCountInline, VisitingInline]

    # US date columns
    def check_in_us(self, obj):
        return obj.check_in_date.strftime('%m/%d/%Y')
    check_in_us.short_description = 'Check-in'
    check_in_us.admin_order_field = 'check_in_date'

    def check_out_us(self, obj):
        return obj.check_out_date.strftime('%m/%d/%Y')
    check_out_us.short_description = 'Check-out'
    check_out_us.admin_order_field = 'check_out_date'

    def nights_display(self, obj):
        return f"{obj.nights} night{'' if obj.nights == 1 else 's'}"
    nights_display.short_description = "Nights"

    def traveller_breakdown(self, obj):
        count = getattr(obj, 'count', None)
        return str(count) if count else "—"
    traveller_breakdown.short_description = "Travellers"

    def hotel_rating_stars(self, obj):
        return "★" * obj.hotel_rating + "☆" * (5 - obj.hotel_rating)
    hotel_rating_stars.short_description = "Hotel"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('count')


# ------------------------------------------------------------------
# Visiting Admin (standalone)
# ------------------------------------------------------------------
@admin.register(Visiting)
class VisitingAdmin(admin.ModelAdmin):
    list_display = (
        'request_country',
        'traveller', 'tour', 'tour_departure_us',
        'traveller_check_in_us', 'traveller_check_out_us',
        'booked_on', 'has_notes'
    )
    list_filter = ('tour__country', 'tour__adventure_styles', 'booked_on')
    search_fields = ('traveller__name', 'traveller__email', 'tour__title')
    date_hierarchy = 'booked_on'
    readonly_fields = ('booked_on',)

    def tour_departure_us(self, obj):
        return obj.tour_departure_us
    tour_departure_us.short_description = "Tour Departure"

    def traveller_check_in_us(self, obj):
        return obj.traveller_check_in_us
    traveller_check_in_us.short_description = "Check-in"

    def traveller_check_out_us(self, obj):
        return obj.traveller_check_out_us
    traveller_check_out_us.short_description = "Check-out"

    def has_notes(self, obj):
        return bool(obj.notes)
    has_notes.boolean = True
    has_notes.short_description = "Notes?"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'traveller', 'traveller__count', 'tour'
        )
    




@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContactMessage model.
    Displays key fields in list view and enables searching.
    """
    list_display = ['full_name', 'email', 'subject', 'created_at']
    list_filter = ['created_at']
    search_fields = ['full_name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Contact Details', {
            'fields': ('full_name', 'email')
        }),
        ('Message', {
            'fields': ('subject', 'message')
        }),
        ('Timestamp', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )