# api/views.py
from datetime import datetime
from decimal import Decimal
from rest_framework import generics
from .models import (
    Continent,
    AdventureStyle,
    Country,
    TournTrips,
    Destination
    )
from .serializers import (
    ContinentWithCountriesSerializer,
    AdventureStyleSerializer,
    TournTripsSerializer,
    CitySerializer
    )
from django.shortcuts import get_object_or_404
from .pagination import TenPerPagePagination
from django.db.models import QuerySet
from django.db.models import F, ExpressionWrapper, DecimalField, IntegerField
from rest_framework.filters import OrderingFilter
from django.db.models import Prefetch
from rest_framework import generics


class ContinentCountriesView(generics.RetrieveAPIView):
    """
    GET /api/continents/<id>/countries/
    Returns: { id, name, code, countries: [...] }
    """
    
    serializer_class = ContinentWithCountriesSerializer
    lookup_field = 'id'  # or 'code' if you prefer /api/continents/AF/

    def get_queryset(self):
        # Prefetch countries and sort them by name
        return Continent.objects.prefetch_related(
            Prefetch(
                'countries',  # assuming related_name='countries' in Country model
                queryset=Country.objects.order_by('name')  # A-Z sort
            )
        ).all()





# List all adventure styles
class AdventureStyleListView(generics.ListAPIView):
    queryset = AdventureStyle.objects.all().order_by('name')
    serializer_class = AdventureStyleSerializer


# Get one adventure style by ID
class AdventureStyleDetailView(generics.RetrieveAPIView):
    queryset = AdventureStyle.objects.all()
    serializer_class = AdventureStyleSerializer
    lookup_field = 'id'  # or 'name' if you prefer /api/styles/Hiking/


class CountryToursListView(generics.ListAPIView):
    """
    GET /api/countries/<int:country_id>/tours/
    Returns paginated tours for a country.
    """
    serializer_class = TournTripsSerializer
    pagination_class = TenPerPagePagination

    def get_queryset(self):
        country_id = self.kwargs['country_id']
        country = get_object_or_404(Country, id=country_id)
        return TournTrips.objects.filter(country=country).select_related(
            'country', 'adventure_styles'
        ).prefetch_related('destinations').order_by('departure_date')
    


class CountryCitiesListView(generics.ListAPIView):
    """
    GET /tourntrips/countries/<country_id>/cities/
    Returns unique cities from destinations in that country.
    """
    serializer_class = CitySerializer
    # pagination_class = TenPerPagePagination

    def get_queryset(self) -> QuerySet:
        country_id = self.kwargs['country_id']
        country = get_object_or_404(Country, id=country_id)
        # Get distinct cities
        cities = (
            Destination.objects
            .filter(country=country)
            .values_list('city', flat=True)
            .distinct()
            .order_by('city')
        )
        # Convert to list of dicts for serializer
        return [{'city': city} for city in cities]









class CountryToursListView(generics.ListAPIView):

    """
    GET /tourntrips/countries/<country_id>/tours/
    Filters:
      ?price=low      → cheapest first
      ?price=high     → most expensive first
      ?duration=short → shortest trip first
      ?duration=long  → longest trip first
      ?reviews=most   → most reviews first
      ?discount=high  → highest savings first
      ?popularity=high → most popular (rating × reviews)
    
    New Filters:
      ?min_price=100&max_price=1000 → tours with shadow_price in range [min, max]
      ?city_id=123 → tours including the destination with id=123
      ?departure_date=2025-11-05 → tours departing on exact date (YYYY-MM-DD)
      ?month=11 → tours departing in the specified month (1-12)
      ?start_city=New York&end_city=Los Angeles → tours with exact start/end cities
    """

    serializer_class = TournTripsSerializer
    pagination_class = TenPerPagePagination
    filter_backends = [OrderingFilter]

    def get_queryset(self):
        country_id = self.kwargs['country_id']
        country = get_object_or_404(Country, id=country_id)

        queryset = TournTrips.objects.filter(country=country).select_related(
            'country', 'adventure_styles'
        ).prefetch_related('destinations')

        # Apply new filters
        request = self.request

        # Min/Max price filter
        min_price = request.query_params.get('min_price')
        if min_price:
            queryset = queryset.filter(shadow_price__gte=Decimal(min_price))
        
        max_price = request.query_params.get('max_price')
        if max_price:
            queryset = queryset.filter(shadow_price__lte=Decimal(max_price))

        # City ID filter (assumes city_id refers to Destination.id)
        city_id = request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(destinations__id=city_id)

        city_name = request.query_params.get('city_name')      # <-- NEW
        if city_name:
            # case-insensitive contains
            queryset = queryset.filter(destinations__city__icontains=city_name)

        # Specific departure date filter
        departure_date = request.query_params.get('departure_date')
        if departure_date:
            try:
                # date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date()
                # queryset = queryset.filter(departure_date=date_obj)
                pass
            except ValueError:
                # Invalid date format; queryset remains unchanged (or handle error as needed)
                pass

        # Month filter (1-12)
        month = request.query_params.get('month')
        if month:
            try:
                # month_int = int(month)
                # if 1 <= month_int <= 12:
                #     queryset = queryset.filter(departure_date__month=month_int)
                pass
            except ValueError:
                # Invalid month; queryset remains unchanged
                pass


        adventure_style = self.request.query_params.getlist('adventure_style')
        if adventure_style:
            # Convert to ints, ignore invalid
            try:
                ids = [int(aid) for aid in adventure_style if aid.isdigit()]
                if ids:
                    queryset = queryset.filter(adventure_styles__id__in=ids)
            except ValueError:
                pass

        # Start and end city filters (exact match)
        start_city = request.query_params.get('start_city')
        if start_city:
            queryset = queryset.filter(start_city=start_city)

        end_city = request.query_params.get('end_city')
        if end_city:
            queryset = queryset.filter(end_city=end_city)

        # Apply ordering (existing logic)
        filter_param = request.query_params.get('filter')

        if filter_param == 'price=low':
            queryset = queryset.order_by('shadow_price')

        elif filter_param == 'price=high':
            queryset = queryset.order_by('-shadow_price')

        elif filter_param == 'duration=short':
            queryset = queryset.order_by('_nights')

        elif filter_param == 'duration=long':
            queryset = queryset.order_by('-_nights')

        elif filter_param == 'reviews=most':
            queryset = queryset.order_by('-no_of_reviews')

        elif filter_param == 'discount=high':
            # Calculate savings: price * (discount / 100)
            savings = ExpressionWrapper(
                F('shadow_price') * F('discount_percentage') / 100,
                output_field=DecimalField(max_digits=12, decimal_places=2)
            )
            queryset = queryset.annotate(savings=savings).order_by('-savings')

        elif filter_param == 'popularity=high':
            # Popularity = rating × number of reviews
            popularity = ExpressionWrapper(
                F('rating') * F('no_of_reviews'),
                output_field=IntegerField()
            )
            queryset = queryset.annotate(popularity=popularity).order_by('-popularity')

        else:
            # Default: newest departure first
            queryset = queryset.order_by('departure_date')

        return queryset
    







# --------------------------------------------------------------
# GET /api/tours/<int:id>/
# Returns a single tour with all related data (destinations, adventure style, etc.)
# --------------------------------------------------------------
class TourDetailView(generics.RetrieveAPIView):
    """
    GET /api/tours/<int:id>/
    Returns a single TournTrips object with full details.
    """
    queryset = TournTrips.objects.select_related(
        'country', 'adventure_styles'
    ).prefetch_related('destinations')
    serializer_class = TournTripsSerializer
    lookup_field = 'id'








from django.http import JsonResponse
from .models import Country
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def country_by_slug(request):
    slug = request.GET.get('slug')
    if not slug:
        return JsonResponse({'error': 'slug parameter is required'}, status=400)

    try:
        country = Country.objects.get(slug=slug)
        data = {
            'id': country.id,
            'name': country.name,
            'slug': country.slug,
            # add other fields as needed
        }
        return JsonResponse(data)
    except Country.DoesNotExist:
        return JsonResponse({'error': 'Country not found'}, status=404)