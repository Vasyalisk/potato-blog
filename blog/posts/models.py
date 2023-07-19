from django.db import models
from django.db.models import functions


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=320)
    content = models.TextField()

    def __str__(self):
        return f"{self.created_at.isoformat().split('T')[0]}: {self.title}"

    @classmethod
    def with_content_short(cls, queryset: models.QuerySet = None) -> models.QuerySet:
        if queryset is None:
            queryset = cls.objects.all()

        queryset = queryset.annotate(content_short=functions.Left("content", 128))
        return queryset


class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField("posts.Post", related_name="tags")
    name = models.CharField(max_length=255, unique=True)
