import httpx

from app.core.config import settings


async def send_booking_confirmation(
    user_id: str,
    event_id: str
):

    data = {
        "user_id": user_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CONFIRMED",
        "message": "Your booking has been confirmed"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send",
            json=data
        )

        return response.json() 
    

async def send_booking_cancelled(
    user_id: str,
    event_id: str
):

    data = {
        "user_id": user_id,
        "event_id": event_id,
        "notification_type": "BOOKING_CANCELLED",
        "message": "Your booking has been cancelled"
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/notifications/send",
            json=data
        )

        return response.json()