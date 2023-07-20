from django.contrib import admin

import feedback.models


@admin.register(feedback.models.Comment)
class CommentAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("user", "post", "content")}),
        ("Misc", {"fields": ("id", "created_at", "updated_at")}),
        ("Stats", {"fields": ("likes_count",)}),
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "likes_count",
    )
    list_display = ["created_at", "user", "post"]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.with_likes_count().select_related("user", "post")
        return queryset

    def likes_count(self, comment):
        return comment.likes_count


@admin.register(feedback.models.PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    fields = ("id", "created_at", "post", "user")
    list_display = ("created_at", "post", "user")
    readonly_fields = ("id", "created_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("user", "post")
        return queryset


@admin.register(feedback.models.CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    fields = ("id", "created_at", "comment", "user")
    list_display = ("created_at", "comment", "user")
    readonly_fields = ("id", "created_at")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related("comment", "user")
        return queryset
