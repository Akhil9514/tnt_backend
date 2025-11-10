# views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly  # Adjust as needed (e.g., AllowAny for public)
from .models import Traveller, Visiting
from .serializers import TravellerSerializer, VisitingSerializer

class TravellerListCreateView(generics.ListCreateAPIView):
    """
    GET: List all travellers (paginated).
    POST: Create a new traveller (with optional nested count).
    """
    queryset = Traveller.objects.select_related('count').order_by('-check_in_date')
    serializer_class = TravellerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Example; customize


class TravellerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE: Retrieve/update/delete a specific traveller by ID.
    """
    queryset = Traveller.objects.select_related('count')
    serializer_class = TravellerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VisitingListCreateView(generics.ListCreateAPIView):
    """
    GET: List all bookings/visits (paginated).
    POST: Create a new booking (requires traveller details nested and tour_id; creates Traveller if needed).
    """
    queryset = Visiting.objects.select_related('traveller', 'tour').order_by('-booked_on')
    serializer_class = VisitingSerializer
    # permission_classes = [IsAuthenticatedOrReadOnly]


class VisitingDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH/DELETE: Retrieve/update/delete a specific booking by ID.
    """
    queryset = Visiting.objects.select_related('traveller', 'tour')
    serializer_class = VisitingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]