from django.db import models


class UnsentEmail(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    plain_text = models.TextField()
    html_text = models.TextField()

    reason = models.CharField(max_length=255)


class EmailCredentials(models.Model):
    """
    Model to set up email credentials. Configured for Gmail by default
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    host = models.CharField(max_length=128, default="smtp.gmail.com")
    port = models.IntegerField(default=587)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    from_email = models.EmailField()
    use_tsl = models.BooleanField(default=True)
    use_ssl = models.BooleanField(default=False)
    fail_silently = models.BooleanField(default=False)
    timeout = models.IntegerField(
        default=3600, help_text="Timeout in seconds for blocking operations like the connection attempt"
    )

    are_active = models.BooleanField(
        default=True,
        help_text="If False, those credentials won't be used to send emails",
    )
