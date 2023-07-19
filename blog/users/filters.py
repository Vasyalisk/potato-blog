from django_filters import rest_framework as filters
import users.models


class UserFilterSet(filters.FilterSet):
    username = filters.CharFilter(lookup_expr="icontains")
    sort_by = filters.OrderingFilter(fields=["username"])

    class Meta:
        model = users.models.User
        fields = []
