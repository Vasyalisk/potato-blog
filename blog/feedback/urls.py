from django.urls import path
from rest_framework.routers import SimpleRouter

from feedback import views

router = SimpleRouter()
router.register("comments", views.CommentViewSet, basename="comment")

urlpatterns = [
    *router.urls,
    path("posts/<int:id>/change_like/", views.PostLikeChangeView.as_view(), name="post-change-like"),
    path("comments/<int:id>/change_like/", views.CommentLikeChange.as_view(), name="comment-change-like"),
]
