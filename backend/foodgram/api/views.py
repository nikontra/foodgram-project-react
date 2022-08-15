from django.db.models import Exists, OuterRef, Subquery, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from foodgram.settings import LIST_SHOP
from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User
from .filters import RecipeFilter
from .mixins import ListCreateRetrieveUpdateDeleteMixin, ListRetrieveMixin
from .paginations import CustomPageNumberRagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FollowSerializer, IngredientsSerializer,
                          RecipeCreateUpdateSerializer, RecipesMiniSerializer,
                          RecipesSerializer, TagsSerializer)


CONTENT_TYPE = 'text/plain'


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет пользователя"""
    http_method_names = ('get', 'post', 'delete',)
    pagination_class = CustomPageNumberRagination

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribers__user=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        user = self.request.user
        follow = Follow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif follow.exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(
                user=user, author=author
            )
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not follow.exists():
            return Response(
                {'errors': 'Вы не подписаны на данного автора'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveMixin):
    """Вьюсет для тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(ListRetrieveMixin):
    """Вьюсет для игредиентов"""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class RecipeViewSet(ListCreateRetrieveUpdateDeleteMixin):
    """Вьюсет для рецептов"""
    http_method_names = ('get', 'post', 'patch', 'delete')
    permission_classes = [IsAuthenticatedOrReadOnly & IsAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberRagination

    def get_queryset(self):
        return Recipe.objects.annotate(
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

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipesSerializer
        return RecipeCreateUpdateSerializer

    @staticmethod
    def add_delete_recipe(model, pk, request):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        existing_object = model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if existing_object.exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipesMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        existing_object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def favorite(self, request, pk):
        return self.add_delete_recipe(
            model=Favorite, pk=pk, request=request
        )

    @action(
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        detail=True
    )
    def shopping_cart(self, request, pk):
        return self.add_delete_recipe(
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
        shopping_cart = '\n'.join([
            f'{ingredient["ingredient__name"]} - {ingredient["total_amount"]}'
            f'{ingredient["ingredient__measurement_unit"]}'
            for ingredient in ingredients
        ])
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={LIST_SHOP}'
        return response
