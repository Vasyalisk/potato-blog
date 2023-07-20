from django.db import models


class CommentQuerySet(models.QuerySet):
    def with_likes_count(self, field_name="likes_count"):
        return self.annotate(**{field_name: models.Count("likes")})


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=255)

    objects = CommentQuerySet.as_manager()

    @classmethod
    def with_likes_count(cls, queryset: models.QuerySet = None) -> models.QuerySet:
        if queryset is None:
            queryset = cls.objects.all()

        queryset = queryset.annotate(likes_count=models.Count("likes"))
        return queryset

    def __str__(self):
        return f"{self.created_at.isoformat().split('T')[0]} {self.user.username} on {self.post.title}"


class PostLike(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="post_likes")

    def __str__(self):
        return f"{self.user.username} on {self.post.title}"


class CommentLike(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey("feedback.Comment", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comment_likes")
