import factory
from factory.django import DjangoModelFactory
import posts.models
import users.factories


class PostFactory(DjangoModelFactory):
    class Meta:
        model = posts.models.Post

    user = factory.SubFactory(users.factories.UserFactory)
    title = factory.Faker("sentence", nb_words=5)
    content = factory.Faker("sentence", nb_words=10)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.tags.add(*extracted)
