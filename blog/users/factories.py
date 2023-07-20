import factory
import users.models
import faker

fake = faker.Faker()

username_list = [fake.unique.word() for _ in range(50)]
email_list = [fake.unique.email() for _ in range(50)]


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = users.models.User

    username = factory.Sequence(lambda n: username_list[n % len(username_list)])
    email = factory.Sequence(lambda n: email_list[n % len(email_list)])
    password = factory.Faker("word")

    is_staff = False
    is_superuser = False
