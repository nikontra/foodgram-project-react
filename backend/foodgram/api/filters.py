import django_filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для модели Recipe"""
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = django_filters.CharFilter(field_name='author__id')
    is_favorited = django_filters.BooleanFilter(
        field_name='is_favorited', widget=BooleanWidget()
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        field_name='is_in_shopping_cart', widget=BooleanWidget()
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart',
            'author', 'tags'
        )
