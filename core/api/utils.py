import os
from logging import getLogger

import httpx
from django.core.cache import cache
from httpx import HTTPStatusError, NetworkError, TimeoutException

logger = getLogger(__name__)


def get_emails_for_notification_from_auth(ids: list[int]) -> dict:
    users: dict[int, str] = {}
    not_found_ids = []

    for user_pk in ids:
        cache_key = f"user_profile_{user_pk}"
        cached_user_info = cache.get(cache_key)
        if cached_user_info:
            users[user_pk] = cached_user_info["email"]
        else:
            not_found_ids.append(user_pk)

    if not_found_ids:
        try:
            with httpx.Client() as client:
                response = client.post(
                    os.getenv("AUTH_URL_FOR_GETTING_NOTIFICATION_EMAILS"),
                    json={"ids": not_found_ids},
                )
                response.raise_for_status()

                for pk, user_info in response.json().items():
                    users[pk] = user_info["email"]
                    cache.set(f"user_profile_{pk}", user_info)

        except HTTPStatusError as e:
            raise RuntimeError(f"HTTP error occurred: {e}") from e
        except NetworkError as e:
            raise RuntimeError(f"Network error occurred: {e}") from e
        except TimeoutException as e:
            raise RuntimeError(f"Timeout error occurred: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e
    return users


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
