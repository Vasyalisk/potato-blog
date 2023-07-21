from settings import *

# noinspection PyUnresolvedReferences
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "test-db",
    }
}

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "TEST_REQUEST_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.MultiPartRenderer",
    ],
}

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
EMAIL_HOST_USER = "test@email.com"
EMAIL_HOST_PASSWORD = "iamtestpassword"
DEFAULT_FROM_EMAIL = "test@email.com"
