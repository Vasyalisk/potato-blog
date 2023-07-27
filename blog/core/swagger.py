from django.conf import settings


def ignore_openapi_view_extensions():
    """
    Utility to ignore some openapi extensions. In particular, drf_spectacular.contrib.rest_framework.ObtainAuthTokenView
    isn't used but causes warning on schema generation
    :return:
    """
    ignored_extensions = getattr(settings, "SPECTACULAR_SETTINGS", {}).get("IGNORED_OPENAPI_VIEW_EXTENSIONS", [])

    from drf_spectacular.extensions import OpenApiViewExtension

    updated_registry = []

    for one in OpenApiViewExtension._registry:
        full_name = f"{one.__module__}.{one.__qualname__}"

        if full_name not in ignored_extensions:
            updated_registry.append(one)

    OpenApiViewExtension._registry = updated_registry
