import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from toursntrips.models import TournTrips  # Replace 'myapp' with your actual Django app name



class Command(BaseCommand):
    help = 'Update shadow_price and discount_percentage with random values for all TourTrips'

    def handle(self, *args, **options):
        # Fetch all instances
        tours = TournTrips.objects.all()
        total = tours.count()
        self.stdout.write(f'Updating {total} TourTrips instances...')

        updated_count = 0
        for tour in tours:
            # Random price: uniform between 10 and 50000, rounded to 2 decimal places
            shadow_price = Decimal(random.uniform(10, 50000)).quantize(Decimal('0.01'))
            tour.shadow_price = shadow_price

            # Random discount: uniform between 10 and 50, rounded to 2 decimal places
            discount = Decimal(random.uniform(10, 50)).quantize(Decimal('0.01'))
            tour.discount_percentage = discount

            tour.save(update_fields=['shadow_price', 'discount_percentage'])
            updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} instances with random prices and discounts.')
        )