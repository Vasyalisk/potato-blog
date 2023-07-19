from django.core.exceptions import ValidationError
from django.db import models
from django_filters import rest_framework as filters

import posts.models


class PostFilterSet(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=["created_at", "title"])
    tags = filters.CharFilter(method="filter_tags")
    title = filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = posts.models.Post
        fields = {
            "user_id": ["exact"],
            "created_at": ["lte", "gte"],
        }

    def filter_tags(self, queryset: models.QuerySet, name, value: str):
        value = value.split(",")

        if len(value) > 3:
            raise ValidationError("At most 3 tags can be specified", code="invalid", params={"value": value})

        tag_subquery = posts.models.Tag(posts__id=models.OuterRef("id"), name__in=value)
        queryset = queryset.annotate(has_tags=models.Exists(tag_subquery)).filter(has_tags=True)
        return queryset
