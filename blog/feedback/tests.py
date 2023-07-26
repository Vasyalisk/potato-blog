import pytest
from django.urls import reverse
from django.utils import timezone

import feedback.factories
import feedback.models
import posts.factories
import users.factories

COMMENT_LIST_URL = reverse("comment-list")
COMMENT_CREATE_URL = reverse("comment-list")
COMMENT_UPDATE_URL = lambda post_id: reverse("comment-detail", kwargs={"pk": post_id})
COMMENT_DELETE_URL = lambda post_id: reverse("comment-detail", kwargs={"pk": post_id})

COMMENT_CHANGE_LIKE_URL = lambda comment_id: reverse("comment-change-like", kwargs={"id": comment_id})
POST_CHANGE_LIKE_URL = lambda post_id: reverse("post-change-like", kwargs={"id": post_id})
POST_LIST_URL = reverse("post-list")
POST_DETAIL_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})


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

    @pytest.mark.parametrize(
        "method,url",
        (
            ("patch", COMMENT_UPDATE_URL(1)),
            ("delete", COMMENT_DELETE_URL(1)),
        ),
    )
    def test_not_found(self, method, url, api_client, db):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 404

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

    def test_comment_create(self, db, api_client):
        post = posts.factories.PostFactory()
        api_client.force_authenticate(post.user)

        body = {
            "content": "abcd",
            "post_id": post.id,
        }
        resp = api_client.post(COMMENT_CREATE_URL, data=body)
        assert resp.status_code == 201
        data = resp.json()
        comment_id = data["id"]

        comment = feedback.models.Comment.objects.get(id=comment_id)
        assert comment.content == body["content"]
        assert comment.post_id == body["post_id"]
        assert comment.user_id == post.user_id

    def test_comment_create_invalid_post_id(self, db, api_client):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)

        body = {
            "content": "abcd",
            "post_id": 0,
        }
        resp = api_client.post(COMMENT_CREATE_URL, data=body)
        assert resp.status_code == 400
        assert not feedback.models.Comment.objects.exists()

    def test_comment_update(self, api_client, comment_list):
        comment = comment_list[0]
        api_client.force_authenticate(comment.user)

        body = {"content": comment.content + "a"}
        resp = api_client.patch(COMMENT_UPDATE_URL(comment.id), data=body)
        assert resp.status_code == 200

        comment.refresh_from_db()
        assert comment.content == body["content"]

    def test_comment_delete(self, api_client, comment_list):
        comment = comment_list[0]
        api_client.force_authenticate(comment.user)

        resp = api_client.delete(COMMENT_DELETE_URL(comment.id))
        assert resp.status_code == 204
        assert not feedback.models.Comment.objects.filter(id=comment.id).exists()


class TestLikes:
    @pytest.mark.parametrize(
        "method,url",
        (
            ("patch", COMMENT_CHANGE_LIKE_URL(1)),
            ("patch", POST_CHANGE_LIKE_URL(1)),
        ),
    )
    def test_unauthorized(self, method, url, api_client, db):
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 401

    @pytest.mark.parametrize(
        "method,url",
        (
            ("patch", COMMENT_CHANGE_LIKE_URL(1)),
            ("patch", POST_CHANGE_LIKE_URL(1)),
        ),
    )
    def test_not_found(self, method, url, api_client, db):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 404

    @pytest.mark.parametrize(
        "old_value,new_value",
        (
            (True, True),
            (False, False),
            (False, True),
            (True, False),
        ),
    )
    def test_comment_change_like(self, old_value, new_value, api_client, db):
        comment = feedback.factories.CommentFactory()
        user = comment.user

        if old_value:
            feedback.factories.CommentLikeFactory(user_id=user.id, comment_id=comment.id)

        api_client.force_authenticate(user)
        body = {"is_liked": new_value}
        resp = api_client.patch(COMMENT_CHANGE_LIKE_URL(comment.id), data=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_liked"] == new_value
        assert feedback.models.CommentLike.objects.filter(comment_id=comment.id, user_id=user.id).exists() == new_value

    @pytest.mark.parametrize(
        "old_value,new_value",
        (
            (True, True),
            (False, False),
            (False, True),
            (True, False),
        ),
    )
    def test_post_change_like(self, old_value, new_value, api_client, db):
        post = posts.factories.PostFactory()
        user = post.user

        if old_value:
            feedback.factories.PostLikeFactory(user_id=user.id, post_id=post.id)

        api_client.force_authenticate(user)
        body = {"is_liked": new_value}
        resp = api_client.patch(POST_CHANGE_LIKE_URL(post.id), data=body)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_liked"] == new_value
        assert feedback.models.PostLike.objects.filter(post_id=post.id, user_id=user.id).exists() == new_value

    @pytest.fixture()
    def liked_comment_list(self, db):
        comments = feedback.factories.CommentFactory.create_batch(3)
        feedback.factories.CommentLikeFactory.create_batch(3, comment_id=comments[0].id)
        return comments

    @pytest.mark.parametrize("index", (0, 1))
    def test_comment_list_likes_count(self, index, api_client, liked_comment_list):
        comment = liked_comment_list[index]
        likes_count = comment.likes.count()

        resp = api_client.get(COMMENT_LIST_URL)
        assert resp.status_code == 200
        data = resp.json()

        comment_data = next(filter(lambda c: c["id"] == comment.id, data["results"]))
        assert comment_data["likes_count"] == likes_count

    @pytest.fixture()
    def liked_post_list(self, db):
        post_list = posts.factories.PostFactory.create_batch(3)
        feedback.factories.PostLikeFactory.create_batch(3, post_id=post_list[0].id)
        return post_list

    @pytest.mark.parametrize("index", (0, 1))
    def test_post_list_likes_count(self, index, api_client, liked_post_list):
        post = liked_post_list[index]

        resp = api_client.get(POST_LIST_URL)
        assert resp.status_code == 200
        data = resp.json()

        likes_count = post.likes.count()
        post_data = next(filter(lambda p: p["id"] == post.id, data["results"]))
        assert post_data["likes_count"] == likes_count

    @pytest.mark.parametrize("index", (0, 1))
    def test_post_detail_likes_count(self, index, api_client, liked_post_list):
        post = liked_post_list[0]

        resp = api_client.get(POST_DETAIL_URL(post.id))
        assert resp.status_code == 200
        data = resp.json()

        likes_count = post.likes.count()
        assert data["likes_count"] == likes_count
