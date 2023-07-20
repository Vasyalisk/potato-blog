from rest_framework.test import APIClient
import pytest


@pytest.fixture()
def api_client():
    client = APIClient()
    return client
