import httpx

from app.core.config import settings


async def verify_token(token: str):

    if not token:
        return None

    headers = {
        "Authorization": token
    }

    async with httpx.AsyncClient() as client:

        response = await client.get(
            f"{settings.REGISTRATION_SERVICE_URL}/verify",
            headers=headers
        )

        if response.status_code != 200:
            return None

        return response.json()