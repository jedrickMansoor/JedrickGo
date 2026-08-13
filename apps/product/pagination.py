from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"

    def paginate_queryset(self, queryset, request, view=None):
        quantity = request.query_params.get("quantity")

        if quantity:
            try:
                quantity = int(quantity)

                if quantity > 0:
                    queryset = queryset[:quantity]

            except (ValueError, TypeError):
                pass

        if "page" not in request.query_params:
            request._request.GET = request._request.GET.copy()
            request._request.GET["page"] = "1"

        return super().paginate_queryset(
            queryset,
            request,
            view
        )