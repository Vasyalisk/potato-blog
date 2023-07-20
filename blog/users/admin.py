from django.contrib import admin
import users.models
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin


@admin.register(users.models.User)
class UserAdmin(DefaultUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Misc", {"fields": ("created_at", "id")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                ),
            },
        ),
    )
    readonly_fields = [
        "id",
        "created_at",
    ]
    list_display = ("created_at", "username", "email", "is_staff")
    list_filter = ("is_staff", "is_superuser", "groups")
    search_fields = ("username", "email")
    filter_horizontal = ("groups",)
