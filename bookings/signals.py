# bookings/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Visiting
from .tasks import send_booking_confirmation_email_task  # Import the task
from django.db import transaction  # ← ADD THIS IMPORT

@receiver(post_save, sender=Visiting)
def queue_booking_confirmation_email(sender, instance, created, **kwargs):
    """
    Queue the email task asynchronously on creation.
    """
    if created:
        # Delay execution until after the transaction commits (optional but recommended)
        transaction.on_commit(lambda: send_booking_confirmation_email_task.delay(instance.id))