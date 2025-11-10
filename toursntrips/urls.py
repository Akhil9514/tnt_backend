"""
URL configuration for tnt_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from .views import (
    ContinentCountriesView,
    AdventureStyleListView,
    AdventureStyleDetailView,
    CountryToursListView,
    CountryCitiesListView,
    TourDetailView
)

urlpatterns = [
    path('continents/<int:id>/countries/', ContinentCountriesView.as_view(), name='continent-countries'),
    path('adventure-styles/', AdventureStyleListView.as_view(), name='adventure-style-list'),
    path('adventure-styles/<int:id>/', AdventureStyleDetailView.as_view(), name='adventure-style-detail'),
    path('countries/<int:country_id>/tours/', CountryToursListView.as_view(), name='country-tours'),
    path('countries/<int:country_id>/cities/', CountryCitiesListView.as_view(), name='country-cities'),
    path('tours/<int:id>/', TourDetailView.as_view(), name='tour-detail'),
    ]