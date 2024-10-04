import jwt
from django.conf import settings
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed


class JWTMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def __call__(self, request):
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                scheme, token = auth_header.split(' ')

                if scheme.lower() != 'bearer':
                    raise AuthenticationFailed(
                        'Authorization header must start with Bearer'
                    )

                payload = jwt.decode(
                    token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
                )

                user_pk = payload.get('user_pk')
                cache_key = f"user_profile_{user_pk}"
                cached_user_info = cache.get(cache_key)

                if cached_user_info:
                    request.user_info = cached_user_info
                else:
                    full_user_info = {
                        'user_pk': int(user_pk),
                        'email': payload.get('sub'),
                        'role': payload.get('role'),
                        'first_name': payload.get('first_name'),
                        'last_name': payload.get('last_name'),
                    }
                    request.user_info = full_user_info

                    user_info = full_user_info.copy()
                    user_info.pop('user_pk', None)

                    cache.set(cache_key, user_info)

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Expired token')
            except jwt.DecodeError:
                raise AuthenticationFailed('Invalid token')
            except Exception as e:
                raise AuthenticationFailed(f'Authentication failed: {str(e)}')
        else:
            request.user_info = None

        response = self.get_response(request)

        return response
