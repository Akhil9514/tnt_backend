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

    class Meta:
        model = TournTrips
        fields = [
            'id', 'title', 'country', 'country_id',
            'duration', 'duration_display', '_days', '_nights',
            'rating', 'no_of_reviews',
            'destinations',
            'shadow_price', 'discount_percentage',
            'departure_date', 'departure_date_us',
            'adventure_style',
            'start_city', 'end_city',
        ]

    def get_destinations(self, obj):
        return list(obj.destinations.values_list('name', flat=True))


class CitySerializer(serializers.Serializer):
    """
    Simple serializer to return unique city names.
    """
    city = serializers.CharField(max_length=255)

    class Meta:
        fields = ['city']