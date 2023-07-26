from django.db import models
from django_filters import rest_framework as filters
from rest_framework.serializers import ValidationError

import posts.models


class PostFilterSet(filters.FilterSet):
    order_by = filters.OrderingFilter(fields=["created_at", "title"])
    tag_ids = filters.CharFilter(
        method="filter_tag_ids", help_text="Comma-separated integers. At most 3 `tag_ids` can be specified"
    )
    title = filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
        help_text="Case-insensitive search",
    )

    class Meta:
        model = posts.models.Post
        fields = {
            "user_id": ["exact"],
            "created_at": ["lte", "gte"],
        }

    def filter_tag_ids(self, queryset: models.QuerySet, name, value: str):
        tag_ids = value.split(",")
        tag_ids = self.validate_tag_ids(tag_ids)

        tag_subquery = posts.models.Tag.objects.filter(posts__id=models.OuterRef("id"), id__in=tag_ids)
        queryset = queryset.annotate(has_tags=models.Exists(tag_subquery)).filter(has_tags=True)

        return queryset

    def validate_tag_ids(self, tag_ids):
        if len(tag_ids) > 3:
            raise ValidationError({"tag_ids": "At most 3 tag_ids can be specified"})

        try:
            value = [int(one) for one in tag_ids]
        except ValueError:
            raise ValidationError({"tag_ids": "All values must be integers"})

        found_ids = posts.models.Tag.objects.filter(id__in=value).values_list("id", flat=True)
        invalid_ids = set(value).difference(found_ids)

        if invalid_ids:
            raise ValidationError({"tag_ids": f"Tags with ids {list(invalid_ids)} don't exist"})

        return tag_ids


class TagFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        lookup_expr="icontains",
        help_text="Case-insensitive search",
    )

    class Meta:
        model = posts.models.Tag
        fields = []
