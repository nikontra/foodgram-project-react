from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from ..recipes.models import Ingredient, IngredientInRecipe, Recipe, Tag
from ..users.models import Follow, User

MIN_VALUE = 1


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериалайзер создания Пользователь"""
    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

        def create(self, validated_data):
            user = User.objects.create(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            return user

        def validate_username(self, value):
            if value.lower() == 'me':
                raise serializers.ValidationError(
                    'Имя пользователя уже занято'
                )
            return value


class UserSerializer(ModelSerializer):
    """Сериалйзер Пользователя"""
    is_subscribed = serializers.SerializerMethodField(
        method_name='subscriber'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def subscriber(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, author=obj).exists()
        )


class FollowSerializer(UserSerializer):
    """Сериалайзер модели Подписка"""
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_count_recipes'
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get("recipes_limit", None)
        if limit is not None:
            recipes = Recipe.objects.filter(author=obj)[:int(limit)]
        else:
            recipes = Recipe.objects.filter(author=obj)
        return RecipesMiniSerializer(
            recipes, many=True, read_only=True
        ).data

    def get_count_recipes(self, obj):
        return obj.recipes.count()


class TagsSerializer(ModelSerializer):
    """Сериалайзер модели Тег"""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsSerializer(ModelSerializer):
    """Сериалaйзер модели Ингредиент"""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeAmountSerializer(ModelSerializer):
    """Сериалайзер Ингредиента с количеством"""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipesSerializer(ModelSerializer):
    """Сериалайзер для модели Рецепт"""
    tags = TagsSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientRecipeAmountSerializer(many=True)
    is_favorited = serializers.BooleanField(default=False)
    is_in_shopping_cart = serializers.BooleanField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )


class RecipeCreateUpdateSerializer(WritableNestedModelSerializer):
    """Сериалайзер для создания и обновления рецепта"""
    ingredients = IngredientRecipeAmountSerializer(many=True)
    author = UserSerializer(read_only=True)
    image = Base64ImageField()
    tags = serializers.ListField(child=serializers.IntegerField())

    class Meta:
        model = Recipe
        depth = 1
        fields = (
            'id', 'author', 'ingredients',
            'tags', 'image', 'name',
            'text', 'cooking_time'
        )

    def validate(self, data):
        ingredients = data['ingredients']
        if not ingredients:
            raise serializers.ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        ingredient_id_list = []
        for ingredient in ingredients:
            if (not Ingredient.objects.filter(
                    id=ingredient['ingredient']['id']).exists()):
                raise serializers.ValidationError(
                    'Такого ингредиента не существует'
                )
            if int(ingredient.get('amount')) < MIN_VALUE:
                raise serializers.ValidationError(
                    'Кол-во ингредиента не может быть меньше единицы'
                )
            ingredient_id_list.append(ingredient['ingredient']['id'])
        if len(ingredient_id_list) != len(set(ingredient_id_list)):
            raise serializers.ValidationError(
                'Ингредиент добавлен в рецепт дважды'
            )

        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Необходимо указать хотя бы один тег')
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise serializers.ValidationError(
                    'Такого тега не существует'
                )

        cooking_time = data['cooking_time']
        if int(cooking_time) < MIN_VALUE:
            raise serializers.ValidationError(
                'Время приготовления не может быть меньше одной минуты'
            )

        return data

    def create_update_recipe(self, ingredients_data, recipe):
        ingredients = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=get_object_or_404(
                    Ingredient, id=ingredient_data['ingredient']['id']
                ),
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        ]
        IngredientInRecipe.objects.bulk_create(ingredients)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validated_data
        )
        recipe.tags.set(tags)
        self.create_update_recipe(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        super().update(instance, validated_data)
        instance.tags.set(tags)
        self.create_update_recipe(ingredients_data, instance)
        return instance

    def to_representation(self, instance):
        return RecipesSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class RecipesMiniSerializer(serializers.ModelSerializer):
    """Сериалайзер Рецептов для Подписок"""
    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image',
            'cooking_time',
        )
