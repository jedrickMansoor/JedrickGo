from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"

    def paginate_queryset(self, queryset, request, view=None):
        page = request.query_params.get("page")
        quantity = request.query_params.get("quantity")

        if quantity:
            try:
                quantity = int(quantity)

                if quantity > 0:
                    queryset = queryset[:quantity]

            except (ValueError, TypeError):
                pass

        if page is None:
            if quantity:
                return list(queryset)

            return None

        return super().paginate_queryset(
            queryset,
            request,
            view
        )