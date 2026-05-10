import httpx

from app.core.config import settings


async def check_availability(event_id: str):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{settings.EVENT_SERVICE_URL}/events/{event_id}/availability"
        )

        return response.json()


async def reserve_seat(event_id: str):

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{settings.EVENT_SERVICE_URL}/events/{event_id}/reserve"
        )

        return response.json() 
    

async def release_seat(event_id: str):

    async with httpx.AsyncClient() as client:

        response = await client.post(
            f"{settings.EVENT_SERVICE_URL}/events/{event_id}/release"
        )

        return response.json()


async def get_event(event_id: str):

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{settings.EVENT_SERVICE_URL}/events/{event_id}"
        )

        if response.status_code != 200:
            return None

        return response.json()