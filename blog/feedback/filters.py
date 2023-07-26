from django_filters import rest_framework as filters

import feedback.models


class CommentFilterSet(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=["created_at", "user__username"])

    class Meta:
        model = feedback.models.Comment
        fields = {"post_id": ["exact"], "created_at": ["gte", "lte"]}
