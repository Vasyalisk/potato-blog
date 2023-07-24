import posts.factories
import pytest
import posts.models
import posts.serializers
from django.urls import reverse

POST_LIST_URL = reverse("post-list")

POST_TITLES = (
    "A post",
    "C post",
    "B post",
)


class TestPosts:
    @pytest.fixture()
    def post_list(self, db) -> list[posts.models.Post]:
        models = [posts.factories.PostFactory(title=one) for one in POST_TITLES]
        return models

    def test_post_list(self, api_client, post_list):
        resp = api_client.get(POST_LIST_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == len(post_list)

        ordered_titles = [one.title for one in post_list[-1::-1]]
        assert [one["title"] for one in data["results"]] == ordered_titles
