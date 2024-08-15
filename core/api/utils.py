import os
from logging import getLogger

import httpx
from httpx import HTTPStatusError, NetworkError, TimeoutException

logger = getLogger(__name__)


def get_emails_for_notification_from_auth(ids: list[int]) -> dict:
    try:
        with httpx.Client() as client:
            response = client.post(
                os.getenv("AUTH_URL_FOR_GETTING_NOTIFICATION_EMAILS"), json={"ids": ids}
            )
            response.raise_for_status()
        users = response.json().get('users')
        return users
    except HTTPStatusError as e:
        raise RuntimeError(f"HTTP error occurred: {e}") from e
    except NetworkError as e:
        raise RuntimeError(f"Network error occurred: {e}") from e
    except TimeoutException as e:
        raise RuntimeError(f"Timeout error occurred: {e}") from e
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {e}") from e


def get_email_for_notification(request, user_pk: int) -> str:
    if request.user_info.get("user_pk") != user_pk:
        email_for_notification = get_emails_for_notification_from_auth(
            ids=[
                user_pk,
            ]
        ).get(str(user_pk))
    else:
        email_for_notification = request.user_info.email
    return email_for_notification
