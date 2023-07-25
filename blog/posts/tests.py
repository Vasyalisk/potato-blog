import pytest
from django.urls import reverse
from django.utils import timezone

import posts.factories
import posts.models
import posts.serializers
import users.factories

POST_LIST_URL = reverse("post-list")
POST_CREATE_URL = reverse("post-list")
POST_DETAIL_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})
POST_UPDATE_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})
POST_DELETE_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})

TAG_LIST_URL = reverse("tag-list")
TAG_CREATE_URL = reverse("tag-list")


class TestPosts:
    @pytest.fixture()
    def post_list(self, db) -> list[posts.models.Post]:
        now_dt = timezone.now()

        # Adding created_at to force default ordering by descending creation time
        post1 = posts.factories.PostFactory(title="A post", created_at=now_dt)
        post2 = posts.factories.PostFactory(
            title="C post",
            created_at=now_dt - timezone.timedelta(seconds=1),
            user_id=post1.user_id,
        )
        post3 = posts.factories.PostFactory(
            title="D post",
            created_at=now_dt - timezone.timedelta(seconds=2),
            user_id=post1.user_id,
        )
        post4 = posts.factories.PostFactory(
            title="B post",
            created_at=now_dt - timezone.timedelta(seconds=3),
        )

        return [post1, post2, post3, post4]

    @pytest.fixture()
    def tag_list(self, post_list):
        tag1, tag2, tag3 = posts.factories.TagFactory.create_batch(3)
        post1, post2, post3, post4 = post_list

        post1.tags.add(tag1)
        post2.tags.add(tag1, tag2)
        post3.tags.add(tag1, tag3)
        post4.tags.add(tag3)

        return [tag1, tag2, tag3]

    @pytest.mark.parametrize(
        "method,url,payload",
        (
            ("post", POST_CREATE_URL, {"title": "a", "content": "b", "tag_ids": []}),
            ("patch", POST_UPDATE_URL(1), {"title": "a", "content": "b", "tag_ids": []}),
            ("delete", POST_DELETE_URL(1), {}),
        ),
    )
    def test_unauthorized(self, method, url, payload, api_client, db):
        resp = getattr(api_client, method)(url, data=payload)
        assert resp.status_code == 401

    @pytest.mark.parametrize(
        "method,url",
        (
            ("delete", POST_DELETE_URL),
            ("patch", POST_UPDATE_URL),
        ),
    )
    def test_modify_not_my_post(self, method, url, api_client, post_list):
        post = post_list[0]
        user = post_list[-1].user
        api_client.force_authenticate(user)

        resp = getattr(api_client, method)(url(post.id), data={})
        assert resp.status_code == 403

    @pytest.mark.parametrize(
        "method,url",
        (
            ("delete", POST_DELETE_URL(1)),
            ("patch", POST_UPDATE_URL(1)),
        ),
    )
    def test_post_not_found(self, method, url, api_client, db):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 404

    def test_post_list(self, api_client, post_list):
        resp = api_client.get(POST_LIST_URL)
        assert resp.status_code == 200
        data = resp.json()

        assert data["count"] == len(post_list)
        ordered_ids = [one.id for one in post_list]
        assert [one["id"] for one in data["results"]] == ordered_ids

    def test_post_list_filter_user(self, api_client, post_list):
        query = {"user_id": post_list[0].user_id}
        resp = api_client.get(POST_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()

        ordered_ids = [one.id for one in post_list[:-1]]
        assert [one["id"] for one in data["results"]] == ordered_ids

    @pytest.mark.parametrize(
        "query,a_slice",
        (
            # Older than 1st post
            ({"created_at__lte": 1}, slice(1, None)),
            # Newer than last post
            ({"created_at__gte": -2}, slice(0, -1)),
            # Created between 1st and last post
            ({"created_at__lte": 1, "created_at__gte": -2}, slice(1, -1)),
        ),
    )
    def test_post_list_filter_created_at(self, query, a_slice, api_client, post_list):
        query = {key: post_list[val].created_at for key, val in query.items()}
        resp = api_client.get(POST_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        ordered_ids = [one.id for one in post_list[a_slice]]
        assert [one["id"] for one in data["results"]] == ordered_ids

    @pytest.mark.parametrize("order_by", ("created_at", "-created_at", "title", "-title"))
    def test_post_list_order_by(self, order_by, api_client, post_list):
        query = {"order_by": order_by}
        resp = api_client.get(POST_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()

        sort_by = order_by
        is_reversed = False

        if order_by.startswith("-"):
            sort_by = order_by[1:]
            is_reversed = True

        key = lambda p: getattr(p, sort_by)

        ordered_ids = [one.id for one in sorted(post_list, key=key, reverse=is_reversed)]
        assert [one["id"] for one in data["results"]] == ordered_ids

    @pytest.mark.parametrize(
        "tag_indexes,post_indexes",
        (
            ([0], range(3)),
            ([1], [1]),
            ([1, 2], range(1, 4)),
            (range(3), range(4)),
        ),
    )
    def test_post_list_filter_tag_ids(self, tag_indexes, post_indexes, api_client, post_list, tag_list):
        tag_ids = map(lambda i: tag_list[i].id, tag_indexes)
        post_ids = list(map(lambda i: post_list[i].id, post_indexes))

        query = {"tag_ids": ",".join(map(str, tag_ids))}
        resp = api_client.get(POST_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert data["count"] == len(post_ids)
        assert [one["id"] for one in data["results"]] == post_ids

    @pytest.mark.parametrize("title", ("po", "pO", "a", "ac"))
    def test_post_list_filter_title(self, title, api_client, post_list):
        query = {"title": title}
        resp = api_client.get(POST_LIST_URL, data=query)
        assert resp.status_code == 200

        post_ids = list(map(lambda p: p.id, filter(lambda p: title.lower() in p.title.lower(), post_list)))
        data = resp.json()
        assert [one["id"] for one in data["results"]] == post_ids
        assert data["count"] == len(post_ids)

    def test_post_create(self, db, api_client):
        tag = posts.factories.TagFactory()
        user = users.factories.UserFactory()
        payload = {
            "title": "Test post",
            "content": "abcd",
            "tag_ids": [tag.id],
        }

        api_client.force_authenticate(user)
        resp = api_client.post(POST_CREATE_URL, data=payload)
        assert resp.status_code == 201

        data = resp.json()
        post_id = data["id"]
        post = posts.models.Post.objects.get(id=post_id)
        assert post.title == payload["title"]
        assert post.content == payload["content"]
        assert list(map(lambda t: t.id, post.tags.all())) == payload["tag_ids"]

    def test_post_create_invalid_tag(self, db, api_client):
        user = users.factories.UserFactory()
        payload = {
            "title": "Test post",
            "content": "abcd",
            "tag_ids": [1],
        }
        api_client.force_authenticate(user)
        resp = api_client.post(POST_CREATE_URL, data=payload)
        assert resp.status_code == 400
        assert not posts.models.Post.objects.exists()

    def test_post_detail(self, api_client, post_list, tag_list):
        post = post_list[0]
        resp = api_client.get(POST_DETAIL_URL(post.id))
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == post.id
        assert list(map(lambda t: t["id"], data["tags"])) == list(map(lambda t: t.id, post.tags.all()))

    @pytest.mark.parametrize(
        "field,value",
        (
            ("title", "Test"),
            ("content", "Test"),
        ),
    )
    def test_post_update(self, field, value, api_client, post_list):
        post = post_list[0]
        user = post.user
        api_client.force_authenticate(user)

        resp = api_client.patch(POST_UPDATE_URL(post.id), data={field: value})
        assert resp.status_code == 200

        post.refresh_from_db()
        assert getattr(post, field) == value

    @pytest.mark.parametrize(
        "indexes",
        (
            [0],
            [1, 2],
            [],
            [0, 2],
        ),
    )
    def test_post_update_tag_ids(self, indexes, api_client, tag_list, post_list):
        post = post_list[0]
        tag_ids = [tag_list[i].id for i in indexes]

        payload = {"tag_ids": tag_ids}
        api_client.force_authenticate(post.user)
        resp = api_client.patch(POST_UPDATE_URL(post.id), data=payload)
        assert resp.status_code == 200

        data = resp.json()
        assert [one["id"] for one in data["tags"]] == tag_ids

        post.refresh_from_db()
        assert list(post.tags.values_list("id", flat=True)) == tag_ids

    def test_post_delete(self, api_client, post_list):
        post = post_list[0]
        api_client.force_authenticate(post.user)

        resp = api_client.delete(POST_DELETE_URL(post.id))
        assert resp.status_code == 204

        assert not posts.models.Post.objects.filter(id=post.id).exists()


class TestTags:
    @pytest.fixture()
    def tag_list(self, db):
        tag1 = posts.factories.TagFactory(name="bat")
        tag2 = posts.factories.TagFactory(name="cat")
        tag3 = posts.factories.TagFactory(name="dog")

        return [tag1, tag2, tag3]

    @pytest.mark.parametrize("method,url", (("post", TAG_CREATE_URL),))
    def test_unauthorized(self, method, url, api_client, db):
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 401

    def test_tags_list(self, api_client, tag_list):
        resp = api_client.get(TAG_LIST_URL)
        assert resp.status_code == 200

        data = resp.json()
        tag_ids = [one.id for one in tag_list]
        assert [one["id"] for one in data["results"]] == tag_ids

    @pytest.mark.parametrize(
        "name,indexes",
        (
            ("at", [0, 1]),
            ("DoG", [2]),
            ("test", []),
        ),
    )
    def test_tags_list_filter_name(self, name, indexes, api_client, tag_list):
        query = {"name": name}
        resp = api_client.get(TAG_LIST_URL, data=query)
        assert resp.status_code == 200

        data = resp.json()
        assert data["count"] == len(indexes)
        tag_ids = [tag_list[one].id for one in indexes]
        assert [one["id"] for one in data["results"]] == tag_ids

    def test_create_tag(self, api_client, db):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)
        body = {"name": "TeSt"}
        resp = api_client.post(TAG_CREATE_URL, data=body)
        assert resp.status_code == 201

        data = resp.json()
        tag_id = data["id"]
        tag = posts.models.Tag.objects.get(id=tag_id)
        assert tag.name == body["name"].lower()

    def test_create_tag_duplicate(self, api_client, tag_list):
        user = users.factories.UserFactory()
        api_client.force_authenticate(user)

        body = {"name": tag_list[0].name}
        resp = api_client.post(TAG_CREATE_URL, data=body)
        assert resp.status_code == 400
        assert posts.models.Tag.objects.filter(name=tag_list[0].name).count() == 1
