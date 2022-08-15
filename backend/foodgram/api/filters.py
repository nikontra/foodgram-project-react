from django_filters.rest_framework import FilterSet, filters
from django_filters.widgets import BooleanWidget

from recipes.models import Ingredient, Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe"""

    TAG_CHOICES = tuple([(tag.slug, tag.slug) for tag in Tag.objects.all()])

    tags = filters.MultipleChoiceFilter(
        field_name='tags__slug', choices=TAG_CHOICES
    )
    author = filters.CharFilter(field_name='author__id')
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited', widget=BooleanWidget()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart', widget=BooleanWidget()
    )

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart',
            'author', 'tags'
        )


class IngredientFilter(FilterSet):
    name = filters.CharFilter(
        field_name='name', lookup_expr='icontains'
    )

    class Meta:
        model = Ingredient
        fields = ('name',)
