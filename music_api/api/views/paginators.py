from rest_framework.pagination import PageNumberPagination


class Paginator(PageNumberPagination):
    page_size = 200
