from django.contrib import admin

import emails.models


@admin.register(emails.models.UnsentEmail)
class UnsentEmailAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("user", "reason")}),
        ("Misc", {"fields": ("id", "created_at", "updated_at")}),
        ("Content", {"fields": ("subject", "plain_text", "html_text"), "classes": ("collapsed",)}),
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    list_display = (
        "created_at",
        "user",
        "subject",
        "reason",
    )
    search_fields = ("user__email", "user__username", "subject")
    list_filter = ("reason",)


@admin.register(emails.models.EmailCredentials)
class EmailCredentialsAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("host", "port", "username", "password", "from_email")}),
        ("Misc", {"fields": ("id", "created_at", "updated_at", "are_active")}),
        ("Extra", {"fields": ("use_tsl", "use_ssl", "fail_silently", "timeout")}),
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    list_display = (
        "created_at",
        "from_email",
        "are_active",
    )
    ordering = ("are_active", "-created_at")
    search_fields = ("host", "username", "from_email")
    list_filter = ("are_active", "from_email")
