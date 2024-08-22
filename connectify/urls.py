from django.urls import path

from connectify.views import (
    MyFollowersAPIView, MyFollowingAPIView,
    FollowAPIView, RecipeRateAPIView,
    ReviewAPIView, ReviewDeleteAPIView, MyFavouriteAPIView
)

urlpatterns = [
    path('my-followers', MyFollowersAPIView.as_view(), name='my-followers'),
    path('my-following', MyFollowingAPIView.as_view(), name='my-following'),
    path('follow', FollowAPIView.as_view(), name='follow'),
    path('recipes-rate', RecipeRateAPIView.as_view(), name='recipes-rate'),
    path('reviews', ReviewAPIView.as_view(), name='reviews'),
    path('reviews/<int:pk>/delete', ReviewDeleteAPIView.as_view(), name='reviews-delete'),
    path('my-favourites', MyFavouriteAPIView.as_view(), name='my-favourites'),
]