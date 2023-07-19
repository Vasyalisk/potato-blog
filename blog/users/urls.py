from rest_framework.routers import SimpleRouter
from django.urls import path
from users import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django_rest_passwordreset.views import ResetPasswordRequestToken, ResetPasswordConfirm

router = SimpleRouter(trailing_slash=False)
router.register("users", views.UserViewSet, basename="user")


urlpatterns = [
    *router.urls,
    path("auth/register", views.RegisterView.as_view(), name="auth-register"),
    path('auth/login', TokenObtainPairView.as_view(), name='auth-login'),
    path('auth/refresh', TokenRefreshView.as_view(), name='auth-refresh'),
    path("auth/reset_password", ResetPasswordRequestToken.as_view(), name="auth-reset-password"),
    path("auth/reset_password_confirm", ResetPasswordConfirm.as_view(), name="auth-reset-password-confirm"),
    path("auth/change_password", views.ChangePasswordView.as_view(), name="auth-change-password"),
]
