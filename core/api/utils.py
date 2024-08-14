import os
from logging import getLogger

import httpx
from httpx import HTTPStatusError, NetworkError, TimeoutException

logger = getLogger(__name__)


async def get_emails_for_notification(ids: list[int]) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("AUTH_URL_FOR_GETTING_NOTIFICATION_EMAILS"), json={"ids": ids}
            )
            response.raise_for_status()
        users = response.json().get('users')
        return users
    except HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
    except NetworkError as e:
        logger.error(f"Network error occurred: {e}")
    except TimeoutException as e:
        logger.error(f"Timeout error occurred: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
