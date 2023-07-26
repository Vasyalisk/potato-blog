from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

router = SimpleRouter()
router.register("users", views.UserViewSet, basename="user")


urlpatterns = [
    *router.urls,
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/reset_password/", views.ResetPasswordView.as_view(), name="auth-reset-password"),
    path("auth/reset_password_confirm/", views.ResetPasswordConfirmView.as_view(), name="auth-reset-password-confirm"),
    path("auth/change_password/", views.ChangePasswordView.as_view(), name="auth-change-password"),
]
