from django.urls import reverse
import users.factories
import pytest

USER_LIST_URL = reverse("user-list")

USERNAMES = ["superman", "flash", "batman"]


class TestUsers:
    @pytest.fixture()
    def user_list(self, db):
        return [users.factories.UserFactory(username=one) for one in USERNAMES]

    def test_user_list(self, db, api_client, user_list):
        resp = api_client.get(USER_LIST_URL)

        assert resp.status_code == 200
        assert resp.data["count"] == len(user_list)

    @pytest.mark.parametrize("search,resp_usernames", [
        ("fla", {"flash"}),
        ("FlA", {"flash"}),
        ("batman", {"batman"}),
        ("a", set(USERNAMES)),
        ("invalid", set()),
    ])
    def test_user_list_filter_username(self, search, resp_usernames, db, api_client, user_list):
        resp = api_client.get(USER_LIST_URL, data={"username": search})
        assert resp.status_code == 200
        assert resp_usernames == {one["username"] for one in resp.data["results"]}

    @pytest.mark.parametrize("sort_by,resp_usernames", [
        ("username", sorted(USERNAMES)),
        ("-username", sorted(USERNAMES, reverse=True)),
    ])
    def test_user_list_sort(self, sort_by, resp_usernames, db, api_client, user_list):
        resp = api_client.get(USER_LIST_URL, data={"sort_by": sort_by})
        assert resp.status_code == 200
        assert resp_usernames == [one["username"] for one in resp.data["results"]]

    def test_user_list_sort_invalid(self, db, api_client):
        resp = api_client.get(USER_LIST_URL, data={"sort_by": "invalid"})
        assert resp.status_code == 400
