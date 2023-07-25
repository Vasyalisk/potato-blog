import posts.factories
import pytest
import posts.models
import posts.serializers
from django.urls import reverse
from django.utils import timezone

POST_LIST_URL = reverse("post-list")


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

    @pytest.mark.parametrize("query,a_slice", (
            # Older than 1st post
            ({"created_at__lte": 1}, slice(1, None)),

            # Newer than last post
            ({"created_at__gte": -2}, slice(0, -1)),

            # Created between 1st and last post
            ({"created_at__lte": 1, "created_at__gte": -2}, slice(1, -1)),
    ))
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

    @pytest.fixture()
    def tag_list(self, post_list):
        tag1, tag2, tag3 = posts.factories.TagFactory.create_batch(3)
        post1, post2, post3, post4 = post_list

        post1.tags.add(tag1)
        post2.tags.add(tag1, tag2)
        post3.tags.add(tag1, tag3)
        post4.tags.add(tag3)

        return [tag1, tag2, tag3]

    @pytest.mark.parametrize("tag_indexes,post_indexes", (
            ([0], range(3)),
            ([1], [1]),
            ([1, 2], range(1, 4)),
            (range(3), range(4)),
    ))
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

        post_ids = list(map(
            lambda p: p.id, filter(
                lambda p: title.lower() in p.title.lower(), post_list
            )
        ))
        data = resp.json()
        assert [one["id"] for one in data["results"]] == post_ids
        assert data["count"] == len(post_ids)
