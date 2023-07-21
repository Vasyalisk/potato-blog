from django.contrib import admin
from django.core.mail.message import EmailMultiAlternatives

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
    actions = ["resend_emails"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user")
        return queryset

    @admin.action(description="Re-send selected emails")
    def resend_emails(self, request, queryset):
        sent_count = 0
        total_count = queryset.count()

        for model in queryset:
            email = EmailMultiAlternatives(
                subject=model.subject,
                body=model.plain_text,
                to=[model.user.email],
            )
            email.attach_alternative(model.html_text, "text/html")
            sent_count += email.send(fail_silently=True)

        queryset.delete()
        msg = f"Successfully sent {sent_count} emails out of {total_count} requested"
        self.message_user(request, message=msg)


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
