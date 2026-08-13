from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"

    def paginate_queryset(self, queryset, request, view=None):
        page = request.query_params.get(self.page_query_param)

        if page is None:
            return None

        return super().paginate_queryset(
            queryset,
            request,
            view
        )