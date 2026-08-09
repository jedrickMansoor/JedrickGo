from django_filters import rest_framework as filters
from apps.user.models import User

class UserFilter(filters.FilterSet):
    city = filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = User
        fields = ["city"]