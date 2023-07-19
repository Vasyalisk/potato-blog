from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


def get_swagger_view(patterns: list):
    info = openapi.Info(
        title="Blog API",
        description="Simple blog API implementation",
        default_version="v1",
    )

    view = get_schema_view(info, public=True, permission_classes=[permissions.AllowAny], patterns=patterns)
    # noinspection PyUnresolvedReferences
    return view.with_ui("swagger", cache_timeout=0)
