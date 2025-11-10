# serializers.py
from rest_framework import serializers
from .models import Traveller, TravellerCount, Visiting
from toursntrips.models import TournTrips  # Assuming TournTrips is in toursntrips app

class TravellerCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravellerCount
        fields = ['adults', 'children', 'infants']
        read_only_fields = []  # All fields are writable on creation/update


class TravellerSerializer(serializers.ModelSerializer):
    count = TravellerCountSerializer(required=False)  # Nested OneToOne
    nights = serializers.ReadOnlyField()  # Computed property

    class Meta:
        model = Traveller
        fields = [
            'id', 'name', 'phone_number', 'email', 'nationality',
            'check_in_date', 'check_out_date', 'hotel_rating', 'is_direct_flight',
            'count', 'nights'
        ]
        read_only_fields = ['id', 'nights']

    def create(self, validated_data):
        # Handle nested TravellerCount
        count_data = validated_data.pop('count', None)
        traveller = Traveller.objects.create(**validated_data)
        if count_data:
            TravellerCount.objects.create(traveller=traveller, **count_data)
        return traveller

    def update(self, instance, validated_data):
        # Handle nested TravellerCount update
        count_data = validated_data.pop('count', None)
        super().update(instance, validated_data)
        if count_data:
            instance.count.update(**count_data)
        return instance


class VisitingSerializer(serializers.ModelSerializer):
    traveller = TravellerSerializer(required=False)  # Nested writable for creation
    tour = serializers.PrimaryKeyRelatedField(queryset=TournTrips.objects.all())  # Or nested if needed
    tour_title = serializers.CharField(source='tour.title', read_only=True)  # For convenience
    booked_on_formatted = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Visiting
        fields = [
            'id', 'request_country', 'traveller', 'tour', 'tour_title', 'booked_on', 'booked_on_formatted', 'notes'
        ]
        read_only_fields = ['id', 'booked_on', 'tour_title', 'booked_on_formatted']

    def create(self, validated_data):
        # Handle nested Traveller creation
        traveller_data = validated_data.pop('traveller', None)
        notes = validated_data.pop('notes', '')

        if traveller_data is not None:
            traveller_serializer = TravellerSerializer(data=traveller_data)
            if traveller_serializer.is_valid():
                traveller_instance = traveller_serializer.save()
            else:
                raise serializers.ValidationError(traveller_serializer.errors)
            validated_data['traveller'] = traveller_instance

        validated_data['notes'] = notes
        return super().create(validated_data)