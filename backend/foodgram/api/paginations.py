from rest_framework.pagination import PageNumberPagination


class CustomPageNumberRagination(PageNumberPagination):
    page_size_query_param = 'limit'
