"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from core.swagger import ignore_openapi_view_extensions

# Remove unused extensions which cause warnings
ignore_openapi_view_extensions()

urlpatterns = [
    path("api/", include("users.urls")),
    path("api/", include("posts.urls")),
    path("api/", include("feedback.urls")),
]

urlpatterns += [
    path("admin/", admin.site.urls),
    path("schema/", SpectacularAPIView.as_view(patterns=urlpatterns[:]), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
