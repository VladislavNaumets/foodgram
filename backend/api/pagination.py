from rest_framework.pagination import PageNumberPagination

from constants.pagination_constants import MAX_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    """Пагинация через ?limit={число}."""
    MAX_PAGE_SIZE = MAX_PAGE_SIZE

    def get_page_size(self, request):
        limit = request.query_params.get("limit", self.page_size)
        try:
            limit = int(limit)
            # Ограничиваем значение limit максимальным пределом
            return min(limit, self.MAX_PAGE_SIZE)
        except ValueError:
            return self.page_size
