import factory
from factory.django import DjangoModelFactory

import posts.models
import users.factories


class TagFactory(DjangoModelFactory):
    class Meta:
        model = posts.models.Tag

    name = factory.Sequence(lambda n: f"Tag {n}")

    @factory.post_generation
    def posts(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        self.posts.add(*extracted)


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

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        created_at = kwargs.pop("created_at", None)
        obj = super()._create(target_class, *args, **kwargs)

        # Setting custom created_at if needed, since y default Django will ignore any auto_now_add field
        if created_at is not None:
            obj.created_at = created_at
            obj.save()

        return obj
