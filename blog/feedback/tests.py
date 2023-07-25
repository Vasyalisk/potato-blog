import pytest
from django.urls import reverse
from django.utils import timezone
import feedback.factories

POST_CREATE_URL = reverse("post-list")
POST_UPDATE_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})
POST_DELETE_URL = lambda post_id: reverse("post-detail", kwargs={"pk": post_id})


class TestComments:
    @pytest.fixture()
    def comment_list(self, db):
        now_dt = timezone.now()
        comment1 = feedback.factories.CommentFactory(created_at=now_dt)
        comment2 = feedback.factories.CommentFactory(
            post_id=comment1.post_id,
            created_at=now_dt - timezone.timedelta(seconds=1)
        )
        comment3 = feedback.factories.CommentFactory(
            user_id=comment2.user_id,
            created_at=now_dt - timezone.timedelta(seconds=2)
        )
        comment4 = feedback.factories.CommentFactory(created_at=now_dt - timezone.timedelta(seconds=3))
        return [comment1, comment2, comment3, comment4]

    @pytest.mark.parametrize("method,url", (
            ("post", POST_CREATE_URL),
            ("patch", POST_UPDATE_URL(1)),
            ("delete", POST_DELETE_URL(1)),
    ))
    def test_unathorized(self, method, url, api_client, db):
        resp = getattr(api_client, method)(url, data={})
        assert resp.status_code == 401

    @pytest.mark.parametrize("method,url", (
            ("patch", POST_UPDATE_URL),
            ("delete", POST_DELETE_URL),
    ))
    def test_modify_not_my_comment(self, method, url, api_client, comment_list):
        comment = comment_list[0]
        user = comment_list[2].user

        api_client.force_authenticate(user)
        resp = getattr(api_client, method)(url(comment.id), data={})
        assert resp.status_code == 403


class TestLikes:
    pass
