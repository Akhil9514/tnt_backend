# bookings/tasks.py
import logging
from celery import shared_task  # ← FIXED: Import from celery, not local app
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from email.mime.image import MIMEImage
from .models import Visiting
import os

logger = logging.getLogger(__name__)  # Logs to Celery worker console

@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email_task(self, visiting_id):
    task_id = self.request.id  # For logging
    logger.info(f"[{task_id}] Task STARTED for Visiting ID: {visiting_id}")
    try:
        # Fetch instance with optimizations
        instance = Visiting.objects.select_related('traveller', 'tour').prefetch_related('tour__destinations').get(id=visiting_id)
        logger.info(f"[{task_id}] Instance LOADED: {instance.traveller.name} -> {instance.tour.title}")

        host_email = getattr(settings, 'HOST_EMAIL', 'vibhakarakhil@gmail.com')
        logger.info(f"[{task_id}] Host email set: {host_email}")

        # Safe pre-fetch
        try:
            _ = instance.traveller.count
            logger.info(f"[{task_id}] Traveller count accessed: {getattr(instance.traveller.count, 'adults', 'N/A')}")
        except Exception as e:
            logger.warning(f"[{task_id}] Traveller count access failed: {e}")

        # Pricing (safe)
        has_price = instance.tour.shadow_price is not None
        if has_price:
            original = instance.tour.shadow_price
            discount = instance.tour.discount_percentage or 0
            final = original * (1 - discount / 100)
            logger.info(f"[{task_id}] Pricing calculated: Original ${original}, Discount {discount}%, Final ${final}")
        else:
            original = discount = final = None
            logger.info(f"[{task_id}] No pricing available")

        # Build context
        context = {
            'traveller_name': instance.traveller.name,
            'traveller_email': instance.traveller.email,
            'traveller_phone': instance.traveller.phone_number,
            'traveller_nationality': instance.traveller.nationality,
            'request_country': instance.request_country,

            'tour_title': instance.tour.title,
            'tour_country': str(instance.tour.country),
            'tour_adventure_style': str(instance.tour.adventure_styles),
            'tour_destinations': ', '.join(str(d) for d in instance.tour.destinations.all()) or 'Various destinations',
            'tour_start_city': instance.tour.start_city,
            'tour_end_city': instance.tour.end_city,
            'tour_duration': instance.tour.duration_display,
            'tour_departure': instance.tour_departure_us,
            'tour_rating': f"{instance.tour.rating} Star" if instance.tour.rating else 'Not specified',

            'check_in_date': instance.traveller_check_in_us,
            'check_out_date': instance.traveller_check_out_us,
            'nights': instance.traveller.nights,
            'traveller_breakdown': str(instance.traveller.count) if hasattr(instance.traveller, 'count') else '1 Adult',
            'hotel_rating': f"{instance.traveller.hotel_rating} Star",
            'direct_flight': 'Yes' if instance.traveller.is_direct_flight else 'No',
            'notes': instance.notes or 'None',

            'has_price': has_price,
            'original_price': f"${original:,.2f}" if has_price else None,
            'discount': f"{discount}%" if has_price else None,
            'final_price': f"${final:,.2f}" if has_price else None,

            'booked_on_us': instance.booked_on.strftime('%m/%d/%Y at %I:%M %p'),

            'company_name': 'Toss & Trips',
            'company_url': 'https://tossntrips.com',
        }
        logger.info(f"[{task_id}] Context PREPARED for {context['traveller_name']}")

        # Render template
        try:
            html_content = render_to_string('bookings/booking_confirmation_email.html', context)
            text_content = strip_tags(html_content)
            logger.info(f"[{task_id}] Template RENDERED (HTML length: {len(html_content)} chars)")
        except Exception as e:
            logger.error(f"[{task_id}] Template rendering FAILED: {e}")
            raise

        # Email setup
        subject = f'Booking Received: {instance.tour.title} - Toss & Trips'
        from_email = settings.DEFAULT_FROM_EMAIL or 'noreply@tossntrips.com'
        to = [instance.traveller.email]
        cc = [host_email] if host_email else []

        logger.info(f"[{task_id}] EMAIL SETUP: To={to}, CC={cc}, From={from_email}, Subject={subject[:50]}...")

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=from_email,
            to=to,
            cc=cc,
        )
        email.attach_alternative(html_content, "text/html")

        # Logo embed
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo.png')
        if os.path.isfile(logo_path):
            with open(logo_path, 'rb') as img:
                logo_image = MIMEImage(img.read())
                logo_image.add_header('Content-ID', '<logo>')
                email.attach(logo_image)
            logger.info(f"[{task_id}] Logo EMBEDDED from {logo_path}")
        else:
            logger.warning(f"[{task_id}] Logo MISSING at {logo_path} (skipping)")

        # Send!
        logger.info(f"[{task_id}] Attempting to SEND email...")
        email.send(fail_silently=False)  # Explicit: raises on failure
        logger.info(f"[{task_id}] Email SENT SUCCESSFULLY to {instance.traveller.email}")
        return f"Email sent successfully to {instance.traveller.email}"

    except Visiting.DoesNotExist:
        logger.error(f"[{task_id}] ERROR: Visiting ID {visiting_id} not found")
        return "Visiting instance not found"
    except Exception as exc:
        logger.error(f"[{task_id}] CRITICAL ERROR: {str(exc)}", exc_info=True)  # Full traceback
        # Retry logic
        retry_countdown = 60 * (2 ** self.request.retries)
        logger.info(f"[{task_id}] RETRYING in {retry_countdown}s (attempt {self.request.retries + 1}/3)")
        raise self.retry(exc=exc, countdown=retry_countdown)