from rest_framework.routers import SimpleRouter
from posts import views

router = SimpleRouter(trailing_slash=False)
router.register("posts", views.PostViewSet, basename="post")
router.register("tags", views.TagViewSet, basename="tag")

urlpatterns = router.urls
