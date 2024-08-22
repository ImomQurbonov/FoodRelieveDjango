from django.urls import path
from .views import (
    RecipesListAPIView, CategoryListAPIView,
    MyRecipesListAPIView, RecipeCreateAPIView,
    RecipeUpdateAPIView, RecipeDeleteAPIView,
    RecipesFilterAPIView, SearchAPIView
)

urlpatterns = [
    path('recipes/', RecipesListAPIView.as_view(), name='recipe-list'),
    path('category-list', CategoryListAPIView.as_view(), name='category-list'),
    path('my-recipe-list', MyRecipesListAPIView.as_view(), name='my-recipe-list'),
    path('recipes-create', RecipeCreateAPIView.as_view(), name='recipe-create'),
    path('recipes/<int:pk>/update/', RecipeUpdateAPIView.as_view(), name='recipe-update'),
    path('recipes/<int:pk>/delete/', RecipeDeleteAPIView.as_view(), name='recipe-delete'),
    path('recipes-filter', RecipesFilterAPIView.as_view(), name='recipes-filter'),
    path('search', SearchAPIView.as_view(), name='search'),
]
