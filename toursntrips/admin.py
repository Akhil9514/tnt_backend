from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Continent, Country, TournTrips, AdventureStyle, Destination
from django.urls import path
from django.http import JsonResponse

class CountryInline(admin.TabularInline):
    model = Country
    extra = 0
    ordering = ['name']


class DestinationInline(admin.TabularInline):
    model = Destination
    extra = 1  # Add one empty form by default
    ordering = ['name']


@admin.register(Continent)
class ContinentAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'code']
    search_fields = ['name', 'code']
    inlines = [CountryInline]
    ordering = ['name']


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'code', 'continent']
    list_filter = ['continent']
    search_fields = ['name', 'code']
    inlines = [DestinationInline]  # Edit destinations inline under country
    ordering = ['name']


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'description_preview']
    list_filter = ['country', 'country__continent']
    search_fields = ['name', 'description', 'country__name', 'city']
    ordering = ['name']

    def description_preview(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else (obj.description or '')
    description_preview.short_description = 'Description Preview'


@admin.register(AdventureStyle)
class AdventureStyleAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'description_preview']  # Preview shows truncated description
    list_display_links = ['pk']  # Makes 'pk' the clickable link to edit form
    search_fields = ['name', 'description']
    list_editable = ['name']  # Only 'name' for inline editing (description edited in detail view)
    ordering = ['name']

    def description_preview(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else (obj.description or '')
    description_preview.short_description = 'Description Preview'



























# from django import forms
# from django.contrib import admin
# from django.urls import path
# from django.http import JsonResponse
# from .models import TournTrips, Destination  # Assuming imports




# class TournTripsAdminForm(forms.ModelForm):
#     class Meta:
#         model = TournTrips
#         fields = '__all__'
#         widgets = {
#             'destinations': forms.SelectMultiple(attrs={'id': 'id_destinations', 'size': 10, 'class': 'vLargeTextField'}),
#             'start_city': forms.Select(attrs={'id': 'id_start_city'}),  # Dropdown, populated by JS
#             'end_city': forms.Select(attrs={'id': 'id_end_city'}),  # Dropdown, populated by JS
#         }
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Default choices with placeholder for both add and edit
#         self.fields['start_city'].choices = [('', '---------')]
#         self.fields['end_city'].choices = [('', '---------')]
#         # For adds: All() so JS PKs validate; JS hides irrelevant via empty()/append
#         # For edits: Pre-filter to instance's country
#         if not self.instance.pk:
#             self.fields['destinations'].queryset = Destination.objects.all()
#         else:
#             country = self.instance.country
#             if country:
#                 self.fields['destinations'].queryset = Destination.objects.filter(country=country)
#             # Pre-populate city choices from instance's destinations for initial display/selection
#             destinations = self.instance.destinations.all()
#             possible_cities = sorted(set(d.city for d in destinations if d.city))
#             self.fields['start_city'].choices = [('', '---------')] + [(city, city) for city in possible_cities]
#             self.fields['end_city'].choices = [('', '---------')] + [(city, city) for city in possible_cities]


#         # ----- NEW: split stored duration into days / nights -----
#         if self.instance.pk and self.instance.duration:
#             try:
#                 nights_str, days_str = self.instance.duration.split(" nights ")
#                 days_str, _ = days_str.split(" days")
#                 self.initial['_days']   = int(days_str)
#                 self.initial['_nights'] = int(nights_str)
#             except Exception:
#                 # malformed string → start with zeros
#                 self.initial['_days']   = 0
#                 self.initial['_nights'] = 0
#         else:
#             self.initial['_days']   = 0
#             self.initial['_nights'] = 0

#     def clean_destinations(self):
#         country = self.cleaned_data.get('country')
#         destinations = self.cleaned_data.get('destinations')  # Already validated objects from to_python()
#         if not country:
#             if destinations:
#                 raise forms.ValidationError("Please select a country before choosing destinations.")
#             return destinations  # Or [] if required=False
#         # Enforce: All selected must belong to country (prevents tampering)
#         invalid_dests = [d for d in destinations if d.country != country]
#         if invalid_dests:
#             valid_names = [d.name for d in Destination.objects.filter(country=country).order_by('name')[:5]]
#             error_msg = f"Destinations must be in {country.name}. Invalid: {[d.name for d in invalid_dests]}. Valid: {', '.join(valid_names)}"
#             if Destination.objects.filter(country=country).count() > 5:
#                 error_msg += "..."
#             raise forms.ValidationError(error_msg)
#         return destinations
    
#     def clean_start_city(self):
#         start_city = self.cleaned_data.get('start_city')
#         destinations = self.cleaned_data.get('destinations')
#         country = self.cleaned_data.get('country')
#         if start_city and country:
#             # Align: Must match a destination's city (string exact match)
#             possible_cities = [d.city for d in destinations] if destinations else []
#             if start_city not in possible_cities:
#                 error_msg = f"Start city '{start_city}' must match a selected destination's city. Possible: {', '.join(set(possible_cities)) or 'None'}"
#                 raise forms.ValidationError(error_msg)
#         return start_city
    
#     def clean_end_city(self):
#         end_city = self.cleaned_data.get('end_city')
#         destinations = self.cleaned_data.get('destinations')
#         country = self.cleaned_data.get('country')
#         if end_city and country:
#             # Align: Must match a destination's city (string exact match)
#             possible_cities = [d.city for d in destinations] if destinations else []
#             if end_city not in possible_cities:
#                 error_msg = f"End city '{end_city}' must match a selected destination's city. Possible: {', '.join(set(possible_cities)) or 'None'}"
#                 raise forms.ValidationError(error_msg)
#         return end_city
   












# @admin.register(TournTrips)
# class TournTripsAdmin(admin.ModelAdmin):
#     form = TournTripsAdminForm

#     list_display = [
#         'title', 'country', 'adventure_styles',
#         'duration_display',               # ← NEW
#         'rating', 'no_of_reviews',
#         'departure_date_us',              # ← US format column
#         'shadow_price',
#         'get_destinations_preview',
#         'start_city', 'end_city',
#     ]

#     list_editable = ['rating', 'no_of_reviews']      # duration is now read-only

#     readonly_fields = ['duration', 'current_start_city', 'current_end_city']

#     fieldsets = (
#         (None, {
#             'fields': (
#                 'title', 'country', 'adventure_styles',
#                 'departure_date', 'shadow_price', 'discount_percentage',
#                 'rating', 'no_of_reviews',
#             )
#         }),

#         ('Duration (edit days / nights → auto-saved as string)', {
#             'fields': ('_days', '_nights'),      # ← NEW fields
#             'description': 'Enter numbers → saved as “X nights Y days” in the “duration” column.',
#         }),

#         ('Update Cities (based on selected destinations)', {
#             'fields': ('destinations', 'start_city', 'end_city'),
#             'classes': ('wide',),
#         }),

#         ('Current Saved Values', {
#             'fields': ('duration', 'current_start_city', 'current_end_city'),
#             'classes': ('wide',),
#         }),
#     )

#     # ------------------------------------------------------------------
#     # US-format column (already defined in the model as a property)
#     # ------------------------------------------------------------------
#     def departure_date_us(self, obj):
#         return obj.departure_date_us
#     departure_date_us.short_description = 'Departure (MM/DD/YYYY)'
#     departure_date_us.admin_order_field = 'departure_date'

#     # ------------------------------------------------------------------
#     # Nice duration column (uses the property)
#     # ------------------------------------------------------------------
#     def duration_display(self, obj):
#         return obj.duration_display
#     duration_display.short_description = 'Duration'

#     def current_start_city(self, obj):
#         return obj.start_city or 'Not set'
#     current_start_city.short_description = 'Saved Start City'

#     def current_end_city(self, obj):
#         return obj.end_city or 'Not set'
#     current_end_city.short_description = 'Saved End City'

#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('ajax/destinations/', self.ajax_destinations_view, name='tourn_trips_ajax_destinations'),
#             path('ajax/possible-cities/', self.ajax_possible_cities_view, name='tourn_trips_ajax_possible_cities'),
#         ]
#         return custom_urls + urls

#     def ajax_destinations_view(self, request):
#         if request.method == 'GET':
#             country_id = request.GET.get('country_id')
#             if country_id:
#                 destinations = Destination.objects.filter(country_id=country_id).values('id', 'name')
#                 data = list(destinations)
#             else:
#                 data = []
#             return JsonResponse(data, safe=False)
#         return JsonResponse({'error': 'Invalid request'}, status=400)

#     def ajax_possible_cities_view(self, request):
#         if request.method == 'GET':
#             dest_ids = request.GET.getlist('dest_ids')  # From multi-select
#             if dest_ids:
#                 destinations = Destination.objects.filter(id__in=dest_ids)
#                 possible_cities = list(set(destinations.values_list('city', flat=True)))  # Unique city names
#                 # Format for JS: [{'id': city, 'name': city}] for option value/text
#                 data = [{'id': city, 'name': city} for city in possible_cities if city]
#             else:
#                 data = []
#             return JsonResponse(data, safe=False)
#         return JsonResponse({'error': 'Invalid request'}, status=400)

#     def get_destinations_preview(self, obj):
#         if obj.destinations.exists():
#             names = [d.name for d in obj.destinations.all()[:3]]
#             preview = ', '.join(names)
#             if len(obj.destinations.all()) > 3:
#                 preview += '...'
#             return preview
#         return 'No destinations'
#     get_destinations_preview.short_description = 'Destinations Preview'

#     class Media:
#         js = (
#             'toursntrips/admin/js/chained_destinations.js',
#             'toursntrips/admin/js/chained_cities_dropdown.js', 
#             'toursntrips/admin/js/update_cities_live.js'
#         )

#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         extra_context = extra_context or {}
#         return super().change_view(request, object_id, form_url, extra_context=extra_context)


        












from django import forms
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django import forms
from .models import TournTrips, Destination, Country  # Assuming imports




class TournTripsAdminForm(forms.ModelForm):
    start_city = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'cities-checkboxes'}),
        required=False
    )
    end_city = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'cities-checkboxes'}),
        required=False
    )

    class Meta:
        model = TournTrips
        fields = '__all__'
        widgets = {
            'destinations': forms.CheckboxSelectMultiple(attrs={'class': 'destinations-checkboxes'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound:
            # For validation on POST, set based on submitted data
            country_id = self.data.get('country')
            if country_id:
                self.fields['destinations'].queryset = Destination.objects.filter(country_id=country_id)
            dest_pks = self.data.getlist('destinations')
            if dest_pks:
                try:
                    dests = Destination.objects.filter(id__in=dest_pks)
                    cities = sorted(set(d.city for d in dests if d.city))
                    self.fields['start_city'].choices = [(city, city) for city in cities]
                    self.fields['end_city'].choices = [(city, city) for city in cities]
                except Exception:
                    self.fields['start_city'].choices = []
                    self.fields['end_city'].choices = []
        else:
            # For unbound (GET), set based on instance
            instance = kwargs.get('instance', None)
            if instance and instance.pk and instance.country:
                self.fields['destinations'].queryset = Destination.objects.filter(country=instance.country)
            if instance and instance.pk:
                destinations = instance.destinations.all()
                possible_cities = sorted(set(d.city for d in destinations if d.city))
                self.fields['start_city'].choices = [(city, city) for city in possible_cities]
                self.fields['end_city'].choices = [(city, city) for city in possible_cities]
                if instance.start_city:
                    self.initial['start_city'] = [instance.start_city]
                if instance.end_city:
                    self.initial['end_city'] = [instance.end_city]
            else:
                self.fields['start_city'].choices = []
                self.fields['end_city'].choices = []

        # ----- NEW: split stored duration into days / nights -----
        if self.instance and self.instance.pk and self.instance.duration:
            try:
                nights_str, days_str = self.instance.duration.split(" nights ")
                days_str, _ = days_str.split(" days")
                self.initial['_days']   = int(days_str)
                self.initial['_nights'] = int(nights_str)
            except Exception:
                # malformed string → start with zeros
                self.initial['_days']   = 0
                self.initial['_nights'] = 0
        else:
            self.initial['_days']   = 0
            self.initial['_nights'] = 0

    def clean_destinations(self):
        country = self.cleaned_data.get('country')
        destinations = self.cleaned_data.get('destinations')  # Already validated objects from to_python()
        if not country:
            if destinations:
                raise forms.ValidationError("Please select a country before choosing destinations.")
            return destinations  # Or [] if required=False
        # Enforce: All selected must belong to country (prevents tampering)
        invalid_dests = [d for d in destinations if d.country != country]
        if invalid_dests:
            valid_names = [d.name for d in Destination.objects.filter(country=country).order_by('name')[:5]]
            error_msg = f"Destinations must be in {country.name}. Invalid: {[d.name for d in invalid_dests]}. Valid: {', '.join(valid_names)}"
            if Destination.objects.filter(country=country).count() > 5:
                error_msg += "..."
            raise forms.ValidationError(error_msg)
        return destinations

    def clean(self):
        cleaned_data = super().clean()
        start_cities = cleaned_data.get('start_city', [])
        end_cities = cleaned_data.get('end_city', [])
        destinations = cleaned_data.get('destinations', [])
        country = cleaned_data.get('country')
        possible_cities = [d.city for d in destinations if d.city]

        if len(start_cities) > 1:
            raise forms.ValidationError({'start_city': "Only one start city can be selected."})
        if start_cities and country and destinations:
            if start_cities[0] not in possible_cities:
                raise forms.ValidationError({'start_city': f"Start city '{start_cities[0]}' must match a selected destination's city. Possible: {', '.join(set(possible_cities)) or 'None'}" })

        if len(end_cities) > 1:
            raise forms.ValidationError({'end_city': "Only one end city can be selected."})
        if end_cities and country and destinations:
            if end_cities[0] not in possible_cities:
                raise forms.ValidationError({'end_city': f"End city '{end_cities[0]}' must match a selected destination's city. Possible: {', '.join(set(possible_cities)) or 'None'}" })

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.start_city = self.cleaned_data.get('start_city', [''])[0] if self.cleaned_data.get('start_city') else ''
        instance.end_city = self.cleaned_data.get('end_city', [''])[0] if self.cleaned_data.get('end_city') else ''
        if commit:
            instance.save()
            self.save_m2m()
        return instance












@admin.register(TournTrips)
class TournTripsAdmin(admin.ModelAdmin):
    form = TournTripsAdminForm

    list_display = [
        'title', 'country', 'adventure_styles',
        'duration_display',               # ← NEW
        'rating', 'no_of_reviews',
        'departure_date_us',              # ← US format column
        'shadow_price',
        'get_destinations_preview',
        'start_city', 'end_city',
    ]

    list_editable = ['rating', 'no_of_reviews']      # duration is now read-only

    readonly_fields = ['duration', 'current_start_city', 'current_end_city']

    fieldsets = (
        (None, {
            'fields': (
                'title', 'country', 'adventure_styles',
                'departure_date', 'shadow_price', 'discount_percentage',
                'rating', 'no_of_reviews',
            )
        }),

        ('Duration (edit days / nights → auto-saved as string)', {
            'fields': ('_days', '_nights'),      # ← NEW fields
            'description': 'Enter numbers → saved as “X nights Y days” in the “duration” column.',
        }),

        ('Update Cities (based on selected destinations)', {
            'fields': ('destinations', 'start_city', 'end_city'),
            'classes': ('wide',),
        }),

        ('Current Saved Values', {
            'fields': ('duration', 'current_start_city', 'current_end_city'),
            'classes': ('wide',),
        }),
    )

    # ------------------------------------------------------------------
    # US-format column (already defined in the model as a property)
    # ------------------------------------------------------------------
    def departure_date_us(self, obj):
        return obj.departure_date_us
    departure_date_us.short_description = 'Departure (MM/DD/YYYY)'
    departure_date_us.admin_order_field = 'departure_date'

    # ------------------------------------------------------------------
    # Nice duration column (uses the property)
    # ------------------------------------------------------------------
    def duration_display(self, obj):
        return obj.duration_display
    duration_display.short_description = 'Duration'

    def current_start_city(self, obj):
        return obj.start_city or 'Not set'
    current_start_city.short_description = 'Saved Start City'

    def current_end_city(self, obj):
        return obj.end_city or 'Not set'
    current_end_city.short_description = 'Saved End City'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('ajax/destinations-checkboxes/', self.ajax_destinations_checkboxes_view, name='tourn_trips_ajax_destinations_checkboxes'),
            path('ajax/cities-checkboxes/', self.ajax_cities_checkboxes_view, name='tourn_trips_ajax_cities_checkboxes'),
        ]
        return custom_urls + urls

    def ajax_destinations_checkboxes_view(self, request):
        if request.method == 'GET':
            country_id = request.GET.get('country_id')
            widget = forms.CheckboxSelectMultiple(attrs={'class': 'destinations-checkboxes'})
            choices = []
            if country_id:
                try:
                    country = Country.objects.get(id=country_id)
                    destinations = Destination.objects.filter(country=country).order_by('name')
                    choices = [(d.id, str(d)) for d in destinations]
                except Country.DoesNotExist:
                    choices = []
            widget.choices = choices
            html = widget.render('destinations', [])
            return JsonResponse({'html': mark_safe(html)})
        return JsonResponse({'error': 'Invalid request'}, status=400)

    def ajax_cities_checkboxes_view(self, request):
        if request.method == 'GET':
            dest_ids = request.GET.getlist('dest_ids')
            field_name = request.GET.get('field_name', 'start_city')
            widget = forms.CheckboxSelectMultiple(attrs={'class': 'cities-checkboxes'})
            choices = []
            if dest_ids:
                destinations = Destination.objects.filter(id__in=dest_ids)
                possible_cities = sorted(set(d.city for d in destinations if d.city))
                choices = [(city, city) for city in possible_cities]
            widget.choices = choices
            html = widget.render(field_name, [])
            return JsonResponse({'html': mark_safe(html)})
        return JsonResponse({'error': 'Invalid request'}, status=400)


    def get_destinations_preview(self, obj):
        if obj.destinations.exists():
            names = [d.name for d in obj.destinations.all()[:3]]
            preview = ', '.join(names)
            if len(obj.destinations.all()) > 3:
                preview += '...'
            return preview
        return 'No destinations'
    get_destinations_preview.short_description = 'Destinations Preview'

    class Media:
        js = (
            'toursntrips/admin/js/checkboxes_destinations.js',
            'toursntrips/admin/js/checkboxes_cities.js', 
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        return super().change_view(request, object_id, form_url, extra_context=extra_context)