import pytest
from rest_framework.response import Response as RestResponse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class AnnotatedResponse(RestResponse):
    """
    Utility class to annotate all possible properties on Django REST response
    """

    def json(self, **kwargs) -> dict:
        ...


class JWTClient(APIClient):
    def force_authenticate(self, user=None, token=None):
        """
        Authenticate user using JWT access token
        :param user:
        :param token:
        :return:
        """
        if user is None:
            self.logout()
            return

        if token is None:
            refresh_token = RefreshToken.for_user(user)
            token = f"Bearer {refresh_token.access_token}"

        self.credentials(HTTP_AUTHORIZATION=token)


@pytest.fixture()
def api_client():
    client = JWTClient()
    return client
