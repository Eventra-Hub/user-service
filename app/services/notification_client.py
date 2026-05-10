import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def _send(data: dict):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send",
                json=data,
            )
            if response.status_code >= 400:
                logger.error(
                    "notification send failed status=%s body=%s payload=%s",
                    response.status_code, response.text, data,
                )
                return None
            return response.json()
    except Exception as e:
        logger.error("notification send error: %s payload=%s", e, data)
        return None


async def send_booking_confirmation(user_id: str, event_id: str):
    return await _send({
        "user_id": user_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CONFIRMED",
        "message": "Your booking has been confirmed",
    })


async def send_booking_cancelled(user_id: str, event_id: str):
    return await _send({
        "user_id": user_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CANCELLED",
        "message": "Your booking has been cancelled",
    })


async def send_organizer_new_booking(organizer_id: str, event_id: str, event_title: str | None = None):
    title = event_title or "your event"
    return await _send({
        "user_id": organizer_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CONFIRMED",
        "message": f"A new attendee booked {title}",
    })


async def send_organizer_booking_cancelled(organizer_id: str, event_id: str, event_title: str | None = None):
    title = event_title or "your event"
    return await _send({
        "user_id": organizer_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CANCELLED",
        "message": f"An attendee cancelled their booking for {title}",
    })