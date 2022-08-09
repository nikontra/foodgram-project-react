from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework import routers
from users.views import CustomUserViewSet

app_name = 'api'

router = routers.DefaultRouter()

router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
]
