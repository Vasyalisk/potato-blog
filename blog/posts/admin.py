from django.contrib import admin

import posts.models


@admin.register(posts.models.Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
        "created_at__day",
        "created_at__year",
        "created_at__month",
    ]
    fieldsets = [
        (None, {"fields": ("title", "user", "content", "tags")}),
        ("Misc", {"fields": ("id", "created_at", "updated_at")}),
        ("Stats", {"fields": ("likes_count", "comments_count")}),
    ]
    readonly_fields = [
        "id",
        "created_at",
        "updated_at",
        "likes_count",
        "comments_count",
    ]
    filter_horizontal = ["tags"]
    list_display = ["created_at", "title", "user"]

    def likes_count(self, post):
        return post.likes_count

    def comments_count(self, post):
        return post.comments_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.with_likes_count().with_comments_count().select_related("user")
        return queryset


@admin.register(posts.models.Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "created_at__day",
        "created_at__year",
        "created_at__month",
    ]
    fields = [
        "id",
        "created_at",
        "name",
        "posts_count",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "posts_count",
    ]
    list_display = ["created_at", "name", "posts_count"]

    def posts_count(self, tag):
        return tag.posts_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.with_posts_count()
        return queryset
