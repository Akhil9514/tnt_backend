from rest_framework import serializers
from .models import (Country, 
                     Continent, 
                     AdventureStyle,
                     Destination,
                     TournTrips
                     )


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']


class ContinentWithCountriesSerializer(serializers.ModelSerializer):
    countries = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Continent
        fields = ['id', 'name', 'code', 'countries']



class AdventureStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdventureStyle
        fields = ['id', 'name', 'description']  # add 'icon' if you enable it
        # fields = '__all__'  # if you want everything



class DestinationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Destination
        fields = ['id', 'name', 'city', 'country']




class TournTripsSerializer(serializers.ModelSerializer):
    country = serializers.CharField(source='country.name', read_only=True)
    country_id = serializers.IntegerField(source='country.id', read_only=True)
    destinations = serializers.SerializerMethodField()
    adventure_style = serializers.CharField(source='adventure_styles.name', read_only=True)

    # Properties → no `source=`
    departure_date_us = serializers.CharField(read_only=True)
    duration_display = serializers.CharField(read_only=True)

    # NEW: Image field with absolute URL (requires request in serializer context)
    image = serializers.SerializerMethodField()

    class Meta:
        model = TournTrips
        fields = [
            'id', 'title', 'country', 'country_id',
            'duration', 'duration_display', '_days', '_nights',
            'rating', 'no_of_reviews',
            'destinations',
            'image',
            'shadow_price', 'discount_percentage',
            'departure_date', 'departure_date_us',
            'adventure_style',
            'start_city', 'end_city',
        ]

    def get_destinations(self, obj):
        return list(obj.destinations.values_list('name', flat=True))
    
    # NEW: Method to return absolute image URL (e.g., http://127.0.0.1:8000/media/tours/filename.jpg)
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                # Build full absolute URL using request (recommended for API responses)
                return request.build_absolute_uri(obj.image.url)
            else:
                # Fallback to relative URL if no request context
                return obj.image.url
        return None  # No image uploaded


class CitySerializer(serializers.Serializer):
    """
    Simple serializer to return unique city names.
    """
    city = serializers.CharField(max_length=255)

    class Meta:
        fields = ['city']