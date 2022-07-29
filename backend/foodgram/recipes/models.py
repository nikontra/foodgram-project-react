from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=15,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'ingredient'
        verbose_name_plural = 'ingredients'

    def __str__(self):
        return self.name


class Tag(models.Model):
    COLOR_CHOICES = (
        ('#E26C2D', 'Orange'),
        ('#49B64E', 'Green'),
        ('#8775D2', 'Purple')
    )

    name = models.CharField(
        max_length=20,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=20,
        choices=COLOR_CHOICES,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Slug тега',
        help_text='Это поле должно быть уникальным!'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'tag'
        verbose_name_plural = 'tags'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    image = models.ImageField(
        verbose_name='Картинка'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    tag = models.ManyToManyField(
        Tag, verbose_name='Тег рецепта'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'recipe'
        verbose_name_plural = 'recipes'

    def __str__(self):
        return self.name


class IngredientRecipeRelation(models.Model):
    """Модель ингредиента указаного в рецепте"""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    amount = models.DecimalField(
        max_digits=6,
        decimal_places=2
    )

    def __str__(self):
        return f'{self.ingredient} для {self.recipe}'


class UserRecipeRelation(models.Model):
    """Модель добавления в избранное"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE
    )
    in_favorites = models.BooleanField(
        default=False
    )
