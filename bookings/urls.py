# urls.py
from django.urls import path
from . import views

app_name = 'travellers'  # Namespace for reverse() calls

urlpatterns = [
    # Traveller URLs
    path('travellers/', views.TravellerListCreateView.as_view(), name='traveller-list-create'),
    path('travellers/<int:pk>/', views.TravellerDetailView.as_view(), name='traveller-detail'),

    # Visiting/Booking URLs
    path('visiting/', views.VisitingListCreateView.as_view(), name='visiting-list-create'),
    path('visits/<int:pk>/', views.VisitingDetailView.as_view(), name='visiting-detail'),

    path('contact/', views.ContactMessageCreateView.as_view(), name='contact-create'),
]