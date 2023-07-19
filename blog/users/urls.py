from rest_framework.routers import SimpleRouter
from users import views

router = SimpleRouter()
router.register("users", views.UserViewSet, basename="user")


urlpatterns = router.urls