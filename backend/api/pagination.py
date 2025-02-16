from rest_framework.pagination import PageNumberPagination

from backend.constants.pagination_constants import PAGE_SIZE


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация."""

    page_size_query_param = 'limit'
    page_size = PAGE_SIZE