import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return None

        try:
            token = token.split(' ')[1]
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            raise AuthenticationFailed('Invalid token')

        user = {
            'user_pk': payload.get('user_pk'),
            'email': payload.get('sub'),
        }
        return user, token
