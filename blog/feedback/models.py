from django.db import models


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comments")
    content = models.CharField(max_length=255)


class PostLike(models.Model):
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="post_likes")


class CommentLike(models.Model):
    comment = models.ForeignKey("feedback.Comment", on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="comment_likes")
