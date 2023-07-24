import factory
from factory.django import DjangoModelFactory

import emails.models
import users.factories


class UnsentEmailFactory(DjangoModelFactory):
    class Meta:
        model = emails.models.UnsentEmail

    user = factory.SubFactory(users.factories.UserFactory)
    subject = "This is test email"
    plain_text = "Test"
    html_text = "<html><body><p>Test</p></body></html>"
    reason = "Fake email"


class EmailCredentialsFactory(DjangoModelFactory):
    class Meta:
        model = emails.models.EmailCredentials

    username = factory.Faker("word")
    password = factory.Faker("word")
    from_email = factory.Faker("email")
