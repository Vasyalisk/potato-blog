from django_filters import rest_framework as filters

import feedback.models


class CommentFilterSet(filters.FilterSet):
    sort_by = filters.OrderingFilter(
        fields=["created_at", "user__username"],
        help_text="Possible values: `created_at`, `-created_at` *(default)*, `user__username`, `-user__username`"
    )

    class Meta:
        model = feedback.models.Comment
        fields = {"post_id": ["exact"], "created_at": ["gte", "lte"]}
