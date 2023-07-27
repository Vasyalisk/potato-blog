import factory
import pytest
from django.core import mail as django_mail
from django.urls import reverse
from django_rest_passwordreset.models import ResetPasswordToken

import users.factories
import users.models

USER_LIST_URL = reverse("user-list")
USER_DETAIL_URL = lambda user_id: reverse("user-detail", kwargs={"pk": user_id})
USER_ME_URL = reverse("user-me")
USER_UPDATE_ME_URL = reverse("user-me")

AUTH_REGISTER_URL = reverse("auth-register")
AUTH_RESET_PASSWORD_URL = reverse("auth-reset-password")
AUTH_CHANGE_PASSWORD_URL = reverse("auth-change-password")

USERNAMES = ["superman", "flash", "batman"]
EMAILS = ["superman@email.com", "flash@email.com", "batman@email.com"]


class TestUsers:
    @pytest.fixture()
    def user_list(self, db):
        return [users.factories.UserFactory(username=USERNAMES[i], email=EMAILS[i]) for i in range(3)]

    def test_user_list(self, db, api_client, user_list):
        resp = api_client.get(USER_LIST_URL)

        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == len(user_list)

    @pytest.mark.parametrize(
        "search,resp_usernames",
        (
            ("fla", {"flash"}),
            ("FlA", {"flash"}),
            ("batman", {"batman"}),
            ("a", set(USERNAMES)),
            ("invalid", set()),
        ),
    )
    def test_user_list_filter_username(self, search, resp_usernames, api_client, user_list):
        resp = api_client.get(USER_LIST_URL, data={"username": search})
        assert resp.status_code == 200
        data = resp.json()
        assert resp_usernames == {one["username"] for one in data["results"]}

    @pytest.mark.parametrize(
        "order_by,resp_usernames",
        (
            ("username", sorted(USERNAMES)),
            ("-username", sorted(USERNAMES, reverse=True)),
        ),
    )
    def test_user_list_sort(self, order_by, resp_usernames, api_client, user_list):
        resp = api_client.get(USER_LIST_URL, data={"order_by": order_by})
        assert resp.status_code == 200
        data = resp.json()
        assert resp_usernames == [one["username"] for one in data["results"]]

    def test_user_list_sort_invalid(self, db, api_client):
        resp = api_client.get(USER_LIST_URL, data={"order_by": "invalid"})
        assert resp.status_code == 400

    def test_user_detail(self, api_client, user_list):
        user = user_list[0]
        assert user.email

        resp = api_client.get(USER_DETAIL_URL(user.id))
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_me"] == False
        assert data["email"] is None
        assert data["id"] == user.id

    def test_user_detail_me(self, api_client, user_list):
        user = user_list[0]
        assert user.email

        api_client.force_authenticate(user)
        resp = api_client.get(USER_DETAIL_URL(user.id))

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["is_me"] == True

    def test_user_me(self, api_client, user_list):
        user = user_list[0]
        api_client.force_authenticate(user)

        resp = api_client.get(USER_ME_URL)
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user.id
        assert data["email"] == user.email
        assert data["is_me"] == True

    def test_user_me_unauthorized(self, db, api_client):
        resp = api_client.get(USER_ME_URL)
        assert resp.status_code == 401

    @pytest.mark.parametrize("updated_field", ("username", "email"))
    def test_user_update_me(self, updated_field, api_client, user_list):
        user = user_list[0]
        api_client.force_authenticate(user)

        updated_value = "a" + getattr(user, updated_field)

        body = {updated_field: updated_value}
        resp = api_client.patch(USER_UPDATE_ME_URL, data=body)
        assert resp.status_code == 200

        user.refresh_from_db()
        assert getattr(user, updated_field) == updated_value

    def test_user_update_me_unauthorized(self, api_client, db):
        body = {"username": "test"}
        resp = api_client.patch(USER_UPDATE_ME_URL, data=body)
        assert resp.status_code == 401

    @pytest.mark.parametrize("unique_field", ("username", "email"))
    def test_update_me_unique(self, unique_field, api_client, user_list):
        user = user_list[0]
        existing_user = user_list[1]

        old_value = getattr(user, unique_field)
        existing_value = getattr(existing_user, unique_field)
        body = {unique_field: existing_value}

        api_client.force_authenticate(user)
        resp = api_client.patch(USER_UPDATE_ME_URL, data=body)
        assert resp.status_code == 400

        user.refresh_from_db()
        assert getattr(user, unique_field) == old_value


class TestAuthorization:
    @pytest.fixture()
    def registered_user(self, db, api_client):
        payload = factory.build(
            dict,
            FACTORY_CLASS=users.factories.UserFactory,
            username=USERNAMES[0],
            email=EMAILS[0],
        )
        user = users.models.User.objects.create_user(**payload)
        user.raw_password = payload["password"]
        return user

    def test_register(self, db, api_client):
        body = {"username": "bob", "password": "1234abcd!", "email": "dylan@email.com"}
        resp = api_client.post(AUTH_REGISTER_URL, data=body)
        assert resp.status_code == 201
        data = resp.json()
        assert "access" in data
        assert "refresh" in data

        user = users.models.User.objects.get(username=body["username"], email=body["email"])
        assert user.password != body["password"]

    def test_register_optional_field(self, db, api_client):
        body = {"username": "bob", "password": "1234abcd!", "email": None}
        resp = api_client.post(AUTH_REGISTER_URL, data=body)
        assert resp.status_code == 201

        user = users.models.User.objects.get(username=body["username"])
        assert user.email is None

    @pytest.mark.parametrize(
        "unique_field,unique_value",
        (
            ("email", EMAILS[0]),
            ("username", USERNAMES[0]),
        ),
    )
    def test_register_unique(self, unique_field, unique_value, api_client, registered_user):
        initial_user_count = users.models.User.objects.count()
        body = {
            "username": "a" + registered_user.username,
            "email": "a" + registered_user.email,
            "password": "1234abcd!",
            **{unique_field: unique_value},
        }
        resp = api_client.post(AUTH_REGISTER_URL, data=body)
        assert resp.status_code == 400
        assert users.models.User.objects.count() == initial_user_count

    def test_reset_password_email_sent(self, api_client, registered_user):
        body = {"email": registered_user.email}
        resp = api_client.post(AUTH_RESET_PASSWORD_URL, data=body)
        assert resp.status_code == 200

        password_reset_token = ResetPasswordToken.objects.get(user_id=registered_user.id)

        last_email = django_mail.outbox[-1]
        assert last_email.to == [registered_user.email]
        assert password_reset_token.key in last_email.body

    def test_reset_password_invalid_email(self, db, api_client):
        body = {"email": "invalid@email.com"}
        resp = api_client.post(AUTH_RESET_PASSWORD_URL, data=body)
        assert resp.status_code == 200
        assert not django_mail.outbox

    def test_change_password(self, api_client, registered_user):
        old_hash = registered_user.password

        api_client.force_authenticate(registered_user)
        body = {"old_password": registered_user.raw_password, "new_password": "1234abcd!"}
        resp = api_client.post(AUTH_CHANGE_PASSWORD_URL, data=body)
        assert resp.status_code == 201

        registered_user.refresh_from_db()
        assert registered_user.password != old_hash

    def test_change_password_invalid(self, api_client, registered_user):
        old_hash = registered_user.password

        api_client.force_authenticate(registered_user)
        body = {"old_password": registered_user.raw_password + "a", "new_password": "1234abcd!"}
        resp = api_client.post(AUTH_CHANGE_PASSWORD_URL, data=body)
        assert resp.status_code == 400

        registered_user.refresh_from_db()
        assert registered_user.password == old_hash
