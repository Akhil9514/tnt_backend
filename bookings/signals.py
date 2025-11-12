# bookings/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Visiting, ContactMessage
from .tasks import send_booking_confirmation_email_task, send_contact_thankyou_email_task


@receiver(post_save, sender=Visiting)
def queue_booking_confirmation_email(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: send_booking_confirmation_email_task.delay(instance.id))


@receiver(post_save, sender=ContactMessage)
def queue_contact_thankyou_email(sender, instance, created, **kwargs):
    """
    Send thank-you email + CC host when a new contact message is saved.
    """
    if created:
        transaction.on_commit(lambda: send_contact_thankyou_email_task.delay(instance.id))