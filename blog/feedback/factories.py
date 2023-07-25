from factory.django import DjangoModelFactory
import factory

import feedback.models
import posts.factories
import users.factories


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = feedback.models.Comment

    user = factory.SubFactory(users.factories.UserFactory)
    post = factory.SubFactory(posts.factories.PostFactory)
    content = factory.Faker("sentence")

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        created_at = kwargs.pop('created_at', None)
        obj = super()._create(target_class, *args, **kwargs)

        # Setting custom created_at if needed, since y default Django will ignore any auto_now_add field
        if created_at is not None:
            obj.created_at = created_at
            obj.save()

        return obj


class CommentLikeFactory(DjangoModelFactory):
    class Meta:
        model = feedback.models.CommentLike

    comment = factory.SubFactory(CommentFactory)
    user = factory.SubFactory(users.factories.UserFactory)


class PostLikeFactory(DjangoModelFactory):
    class Meta:
        model = feedback.models.PostLike

    post = factory.SubFactory(posts.factories.PostFactory)
    user = factory.SubFactory(users.factories.UserFactory)
