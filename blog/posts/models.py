from django.db import models
from django.db.models import functions


class TagQuerySet(models.QuerySet):
    def with_posts_count(self, field_name="posts_count"):
        return self.annotate(**{field_name: models.Count("posts")})


class PostQuerySet(models.QuerySet):
    def with_content_short(self, field_name="content_short"):
        return self.annotate(**{field_name: functions.Left("content", 128)})

    def with_likes_count(self, field_name="likes_count"):
        return self.annotate(**{field_name: models.Count("likes")})

    def with_comments_count(self, field_name="comments_count"):
        return self.annotate(**{field_name: models.Count("comments")})


class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField("posts.Post")
    name = models.CharField(max_length=255, unique=True)

    objects = TagQuerySet.as_manager()

    def __str__(self):
        return self.name


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=320)
    content = models.TextField()

    # workaround to use M2M field in both directions in admin panel
    # noinspection PyUnresolvedReferences
    tags = models.ManyToManyField("posts.Tag", through="posts.tag_posts")

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return f"{self.created_at.isoformat().split('T')[0]}: {self.title}"
