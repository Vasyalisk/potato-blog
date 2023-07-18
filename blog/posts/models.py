from django.db import models


class Post(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=320)
    content = models.TextField()

    def __str__(self):
        return f"{self.created_at.isoformat().split('T')[0]}: {self.title}"


class Tag(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    posts = models.ManyToManyField("posts.Post", related_name="tags")
    name = models.CharField(max_length=255)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    author = models.CharField(max_length=255)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=1024)


class PostLike(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes")


class CommentLike(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)
    comment = models.ForeignKey("posts.Comment", on_delete=models.CASCADE)
