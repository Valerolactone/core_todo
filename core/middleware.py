import jwt
from django.conf import settings
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

                user = {
                    'user_pk': payload.get('user_pk'),
                    'email': payload.get('sub'),
                }
                request.user = user

            except jwt.ExpiredSignatureError:
                raise AuthenticationFailed('Expired token')
            except jwt.DecodeError:
                raise AuthenticationFailed('Invalid token')
            except Exception as e:
                raise AuthenticationFailed(f'Authentication failed: {str(e)}')
        else:
            request.user = None

        response = self.get_response(request)

        return response
