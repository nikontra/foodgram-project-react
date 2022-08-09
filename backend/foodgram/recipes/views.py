from api.filters import RecipeFilter
from api.mixins import ListCreateRetrieveUpdateDeleteMixin, ListRetrieveMixin
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (IngredientsSerializer,
                             RecipeCreateUpdateSerializer,
                             RecipesMiniSerializer, RecipesSerializer,
                             TagsSerializer)
from django.db.models import Exists, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from foodgram.settings import LIST_SHOPPING
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)

CONTENT_TYPE = 'text/plain'


class TagViewSet(ListRetrieveMixin):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(ListRetrieveMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class RecipeViewSet(ListCreateRetrieveUpdateDeleteMixin):
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [IsAuthenticatedOrReadOnly & IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        queryset = Recipe.objects.annotate(
            is_favorited=Exists(
                Subquery(
                    Favorite.objects.filter(
                        user_id=self.request.user.id, recipe__pk=OuterRef('pk')
                    )
                )
            ),
            is_in_shopping_cart=Exists(
                Subquery(
                    ShoppingCart.objects.filter(
                        user_id=self.request.user.id, recipe__pk=OuterRef('pk')
                    )
                )
            ),
        )
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def add_end_delete_recipe(model, pk, request):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if object.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipesMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def favorite(self, request, pk):
        return self.add_end_delete_recipe(
            model=Favorite, pk=pk, request=request
        )

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def shopping_cart(self, request, pk):
        return self.add_end_delete_recipe(
            model=ShoppingCart, pk=pk, request=request
        )

    @action(
        permission_classes=[IsAuthenticated],
        detail=False
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = IngredientInRecipe.objects.filter(
            recipe__users_shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        )
        lines = []

        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            amount = ingredient['total_amount']
            measurement_unit = ingredient['ingredient__measurement_unit']
            lines += f'{name}: {amount} {measurement_unit}\n'

        response = HttpResponse(content_type=CONTENT_TYPE)
        response['Content-Disposition'] = 'attachment;', LIST_SHOPPING
        response.writelines(lines)
        return response
