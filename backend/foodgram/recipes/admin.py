from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1


class IngredientAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientInRecipeInline,)
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(IngredientInRecipe)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
