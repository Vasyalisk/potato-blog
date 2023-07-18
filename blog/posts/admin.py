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
    fields = [
        "created_at",
        "updated_at",
        "title",
        "content",
    ]
    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(posts.models.Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "created_at__day",
        "created_at__year",
        "created_at__month",
    ]
    fields = [
        "created_at",
        "name",
    ]
    readonly_fields = [
        "created_at",
    ]
