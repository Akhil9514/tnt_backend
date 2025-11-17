import random
from decimal import Decimal
from datetime import date
from django.core.management.base import BaseCommand
from toursntrips.models import TournTrips  # Replace 'toursntrips' with your actual Django app name



class Command(BaseCommand):
    help = 'Update departure_date to today for all TourTrips'

    def handle(self, *args, **options):
        # Fetch all instances
        tours = TournTrips.objects.all()
        total = tours.count()
        self.stdout.write(f'Updating {total} TourTrips instances...')

        today = date.today()
        updated_count = 0
        for tour in tours:
            tour.departure_date = today
            tour.save(update_fields=['departure_date'])
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} instances with today\'s date ({today}).')
        )