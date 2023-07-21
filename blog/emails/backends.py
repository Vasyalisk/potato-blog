import smtplib

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend

import emails.models
import users.models


class MultiCredentialEmailBackend(EmailBackend):
    """
    Email sending backend which supports multiple credentials administered via emails.models.EmailCredentials model
    """

    def __init__(self, fail_silently=None):
        self.overrides = {}
        self.from_email = None

        if fail_silently is None:
            self.overrides["fail_silently"] = fail_silently

        super().__init__(fail_silently=fail_silently)

    def set_credentials(self):
        cred_names = [
            "host",
            "port",
            "username",
            "password",
            "use_tls",
            "use_ssl",
            "from_email",
            "fail_silently",
        ]

        creds = emails.models.EmailCredentials.objects.filter(are_active=True).order_by("-created_at").first()

        creds_dict = {one: getattr(creds, one, None) for one in cred_names}
        creds_dict.update(self.overrides)
        [setattr(self, name, val) for name, val in creds_dict.items()]

    def send_messages(self, email_messages):
        self.set_credentials()

        if self.host is None:
            reason = "Email credentials are not set"
            [self.archive_unsent_message(one, reason=reason) for one in email_messages]
            return 0

        return super().send_messages(email_messages)

    def _send(self, email_message: EmailMultiAlternatives) -> bool:
        """
        Send email and return result as bool

        If email_message.to is not specified, message is silently ignored
        :param email_message:
        :return:
        """
        if email_message.from_email is None:
            email_message.from_email = self.from_email

        try:
            is_sent = super()._send(email_message)
        except smtplib.SMTPException as e:
            self.archive_unsent_message(email_message, reason=str(e))
            raise e

        if not is_sent:
            reason = "Failed silently"
            self.archive_unsent_message(email_message, reason=reason)

        return is_sent

    def archive_unsent_message(self, email_message: EmailMultiAlternatives, reason="Unknown"):
        """
        Save email if it contains valid info but wasn't send for some reason
        :param email_message:
        :param reason:
        :return:
        """
        if not email_message.to:
            return

        user = users.models.User.objects.filter(email=email_message.to[0]).first()
        if user is None:
            return

        html_content, _ = email_message.alternatives[0]
        emails.models.UnsentEmail.objects.create(
            user_id=user.id,
            subject=email_message.subject,
            plain_text=email_message.body,
            html_text=html_content,
            reason=reason,
        )
