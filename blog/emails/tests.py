import smtplib
from unittest.mock import MagicMock, patch

import pytest
from django.core.mail import EmailMultiAlternatives

import emails.factories
import emails.models
import users.factories
from emails.backends import MultiCredentialEmailBackend


class TestMultiCredentialEmailBackend:
    @pytest.fixture()
    def smtp_connection_mock(self):
        yield MagicMock()

    @pytest.fixture(autouse=True)
    def emails_backend_mock(self, smtp_connection_mock):
        def _open_smtp_connection_mock(backend):
            backend.connection = smtp_connection_mock
            return True

        def _close_smtp_connection_mock(backend):
            backend.connection = None

        with patch.object(MultiCredentialEmailBackend, "open", _open_smtp_connection_mock) as open_mock, patch.object(
            MultiCredentialEmailBackend, "close", _close_smtp_connection_mock
        ) as close_mock:
            yield {"open": open_mock, "close": close_mock, "connection": smtp_connection_mock}

    @pytest.fixture()
    def smtp_email(self):
        fake_email = emails.factories.UnsentEmailFactory.build()
        email = EmailMultiAlternatives(
            to=[fake_email.user.email],
            subject=fake_email.subject,
            body=fake_email.plain_text,
        )
        email.attach_alternative(fake_email.html_text, "text/html")
        return email

    def test_credentials_are_set(self, db):
        cred = emails.factories.EmailCredentialsFactory()
        be = MultiCredentialEmailBackend()

        param_names = (
            "host",
            "port",
            "username",
            "password",
            "use_tls",
            "use_ssl",
            "timeout",
            "from_email",
            "fail_silently",
        )

        for name in param_names:
            assert getattr(be, name) is None

        be.set_credentials()

        for name in param_names:
            assert getattr(be, name) == getattr(cred, name)

    def test_active_credentials_are_set(self, db):
        emails.factories.EmailCredentialsFactory(are_active=False)
        cred = emails.factories.EmailCredentialsFactory()
        emails.factories.EmailCredentialsFactory(are_active=False)

        be = MultiCredentialEmailBackend()
        be.set_credentials()
        assert be.username == cred.username

    def test_overrides_are_set(self, db):
        override_value = True
        db_value = False

        emails.factories.EmailCredentialsFactory(fail_silently=db_value)
        be = MultiCredentialEmailBackend(fail_silently=override_value)

        assert be.fail_silently is None
        assert be.overrides["fail_silently"] == override_value

        be.set_credentials()
        assert be.fail_silently == override_value

    def test_send_email(self, db, emails_backend_mock, smtp_email):
        emails.factories.EmailCredentialsFactory()
        be = MultiCredentialEmailBackend()
        count = be.send_messages([smtp_email])

        assert count == 1
        assert not emails.models.UnsentEmail.objects.exists()
        emails_backend_mock["connection"].sendmail.assert_called_once()

    @pytest.mark.parametrize("fail_silently", (False, True))
    def test_send_email_failed(self, fail_silently, db, emails_backend_mock, smtp_email):
        emails_backend_mock["connection"].sendmail.side_effect = smtplib.SMTPException()

        users.factories.UserFactory(email=smtp_email.to[0])
        emails.factories.EmailCredentialsFactory(fail_silently=fail_silently)
        be = MultiCredentialEmailBackend()

        exc_raised = False
        count = None
        try:
            count = be.send_messages([smtp_email])
        except smtplib.SMTPException:
            exc_raised = True

        model = emails.models.UnsentEmail.objects.get()

        if fail_silently:
            assert count == 0
            assert not exc_raised
        else:
            assert exc_raised

        assert model.user.email == smtp_email.to[0]
        assert model.plain_text == smtp_email.body
        assert model.subject == smtp_email.subject
        assert model.html_text == smtp_email.alternatives[0][0]

    @pytest.mark.parametrize("fail_silently", (False, True))
    def test_send_email_no_credentials(self, fail_silently, db, smtp_email):
        users.factories.UserFactory(email=smtp_email.to[0])
        be = MultiCredentialEmailBackend(fail_silently=fail_silently)

        exc_raised = False
        count = None
        try:
            count = be.send_messages([smtp_email])
        except ValueError:
            exc_raised = True

        if fail_silently:
            assert not exc_raised
            assert count == 0
        else:
            assert exc_raised

        model = emails.models.UnsentEmail.objects.get()
        assert model.user.email == smtp_email.to[0]
