from django_filters.rest_framework import FilterSet, filters
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    """Фильтр для модели Recipe"""

    TAG_CHOICES = [tag.slug for tag in Tag.objects.all()]
    # TAG_CHOICES = ("",)

    # tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    # tags = filters.CharFilter(max_length=1000, method='filter_tags')
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

    # def filter_tags(self, queryset, name, value):
    #     slugs = value.split(',')
    #     return queryset.filter(
    #         tags__slug__in=slugs
    #     ).order_by('id').distinct('id')

    class Meta:
        model = Recipe
        fields = (
            'is_favorited', 'is_in_shopping_cart',
            'author', 'tags'
        )
