import pytest
from django.urls import reverse
from django.utils import timezone

import feedback.factories

COMMENT_LIST_URL = reverse("comment-list")
COMMENT_CREATE_URL = reverse("comment-list")
COMMENT_UPDATE_URL = lambda post_id: reverse("comment-detail", kwargs={"pk": post_id})
COMMENT_DELETE_URL = lambda post_id: reverse("comment-detail", kwargs={"pk": post_id})


class TestComments:
    @pytest.fixture()
    def comment_list(self, db):
        now_dt = timezone.now()
        comment1 = feedback.factories.CommentFactory(created_at=now_dt)
        comment2 = feedback.factories.CommentFactory(
            post_id=comment1.post_id, created_at=now_dt - timezone.timedelta(seconds=1)
        )
        comment3 = feedback.factories.CommentFactory(
            user_id=comment2.user_id, created_at=now_dt - timezone.timedelta(seconds=2)
        )
        comment4 = feedback.factories.CommentFactory(created_at=now_dt - timezone.timedelta(seconds=3))
        return [comment1, comment2, comment3, comment4]

    @pytest.mark.parametrize(
        "method,url",
        (
            ("post", COMMENT_CREATE_URL),
            ("patch", COMMENT_UPDATE_URL(1)),
            ("delete", COMMENT_DELETE_URL(1)),
        ),
    )
    def test_unathorized(self, method, url, api_client, db):
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 401

    @pytest.mark.parametrize(
        "method,url",
        (
            ("patch", COMMENT_UPDATE_URL),
            ("delete", COMMENT_DELETE_URL),
        ),
    )
    def test_modify_not_my_comment(self, method, url, api_client, comment_list):
        comment = comment_list[0]
        user = comment_list[2].user

        api_client.force_authenticate(user)
        resp = getattr(api_client, method)(url(comment.id), data={})
        assert resp.status_code == 403

    def test_comment_list(self, api_client, comment_list):
        resp = api_client.get(COMMENT_LIST_URL)
        assert resp.status_code == 200

        data = resp.json()
        assert data["count"] == len(comment_list)
        comment_ids = [one.id for one in comment_list]
        assert [one["id"] for one in data["results"]] == comment_ids

    @pytest.mark.parametrize(
        "post_index,comment_indexes",
        (
            (0, [0, 1]),
            (2, [2]),
        ),
    )
    def test_comment_list_filter_post(self, post_index, comment_indexes, api_client, comment_list):
        post_id = comment_list[post_index].post_id
        comment_ids = list(map(lambda i: comment_list[i].id, comment_indexes))

        query = {"post_id": post_id}
        resp = api_client.get(COMMENT_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert [one["id"] for one in data["results"]] == comment_ids

    @pytest.mark.parametrize(
        "query,a_slice",
        (
            ({"created_at__lte": 1}, slice(1, None)),
            ({"created_at__gte": -2}, slice(0, -1)),
            ({"created_at__lte": 1, "created_at__gte": -2}, slice(1, -1)),
        ),
    )
    def test_comment_list_filter_created_at(self, query, a_slice, api_client, comment_list):
        comment_ids = list(map(lambda c: c.id, comment_list[a_slice]))
        query = {k: comment_list[v].created_at for k, v in query.items()}
        resp = api_client.get(COMMENT_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert [one["id"] for one in data["results"]] == comment_ids

    @pytest.mark.parametrize("is_reversed", (True, False))
    def test_comment_list_order_by_created_at(self, is_reversed, api_client, comment_list):
        query = {"order_by": "created_at"}
        comment_ids = list(map(lambda c: c.id, sorted(comment_list, key=lambda c: c.created_at, reverse=is_reversed)))

        if is_reversed:
            query["order_by"] = "-" + query["order_by"]

        resp = api_client.get(COMMENT_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert [one["id"] for one in data["results"]] == comment_ids

    @pytest.mark.parametrize("is_reversed", (True, False))
    def test_comment_list_order_by_username(self, is_reversed, api_client, comment_list):
        query = {"order_by": "user__username"}
        comment_ids = [one.id for one in sorted(comment_list, key=lambda c: c.user.username, reverse=is_reversed)]

        if is_reversed:
            query["order_by"] = "-" + query["order_by"]

        resp = api_client.get(COMMENT_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert [one["id"] for one in data["results"]] == comment_ids


class TestLikes:
    pass
