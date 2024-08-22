from distutils.command.clean import clean

from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.views import get_user_model
from connectify.models import Follow, Rating, Comments, Favorite
from recipes.models import Recipes
from .serializers import (
    FollowListSerializer, RatingSerializer,
    ReviewsSerializer, FollowSerializer,
    FavouriteSerializer
)
from recipes.serializers import RecipesSerializer
User = get_user_model()


class MyFollowingAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowListSerializer

    def get(self, request):
        follow_data = Follow.objects.filter(following=request.user)

        if follow_data.exists():
            followers = User.objects.filter(id__in=follow_data.values_list('followers_id', flat=True))
            followers_serializer = FollowListSerializer(followers, many=True)
            return Response(followers_serializer.data, status=200)
        else:
            return Response({'detail': "Followers not found"}, status=404)


class MyFollowersAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowListSerializer

    def get(self, request):
        follow_data = Follow.objects.filter(followers=request.user)

        if follow_data.exists():
            following = User.objects.filter(
                id__in=follow_data.values_list('following_id', flat=True))
            following_serializer = FollowListSerializer(following, many=True)
            return Response(following_serializer.data, status=200)
        else:
            return Response({'detail': "Following not found"}, status=404)


class FollowAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()

    def post(self, request):
        user = request.user

        try:
            follower_user = User.objects.get(pk=request.data['following'])
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)

        try:
            existing_follow = Follow.objects.get(
                followers=follower_user,
                following=user)
            existing_follow.delete()
            return Response({'detail': "User unfollowed"})
        except Follow.DoesNotExist:
            Follow.objects.create(followers=follower_user, following=user).save()
            return Response({'detail': "User followed"})


class RecipeRateAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RatingSerializer

    def post(self, request, *args, **kwargs):
        try:
            recipe = Recipes.objects.get(pk=request.data['recipe'])
        except Recipes.DoesNotExist:
            return Response({'success': False, 'error': 'Recipe not found'}, status=404)

        rating, created = Rating.objects.update_or_create(
            user=request.user, recipe=recipe,
            defaults={'rating': request.data['rating']}
        )

        serializer = RatingSerializer(rating)
        return Response(serializer.data)


class ReviewAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewsSerializer

    def post(self, request):
        user = request.user
        try:
            recipe = Recipes.objects.get(pk=request.data['recipe'])  # Recipes obyektini olish
        except Recipes.DoesNotExist:
            return Response({'success': False, 'error': 'Recipe not found'}, status=404)

        review = Comments.objects.create(
            user=user,
            recipe=recipe,
            comment=request.data['comment'],
        )
        serializer = ReviewsSerializer(review)
        return Response(serializer.data)


class ReviewDeleteAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ReviewsSerializer
    queryset = Comments.objects.all()

    def delete(self, request, pk):
        user = request.user
        review = Comments.objects.get(pk=pk, user=user)
        if review:
            review.delete()
            return Response({'detail': "Review deleted"}, status=200)

        return Response({'detail': "Review does not exist"}, status=404)


class MyFavouriteAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavouriteSerializer
    queryset = Favorite.objects.all()

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Not authenticated'}, status=401)

        favourites = Favorite.objects.filter(user=request.user)
        if not favourites:
            return Response({'detail': 'My favourite empty !!!'}, status=404)
        recipe_ids = [favourite.recipe_id for favourite in favourites]
        recipes = Recipes.objects.filter(id__in=recipe_ids)
        serializer = RecipesSerializer(recipes, many=True)
        return Response(serializer.data)

    def post(self, request):

        if not request.user.is_authenticated:
            return Response({'detail': 'Not authenticated'}, status=401)

        try:
            recipe = Recipes.objects.get(pk=request.data['recipe'])
        except Recipes.DoesNotExist:
            return Response({'detail': 'Recipe not found'}, status=404)

        favourites = Favorite.objects.filter(user=request.user, recipe=recipe)

        if favourites.exists():
            favourites.delete()
            return Response({'detail': "Favourites deleted"}, status=200)
        else:
            Favorite.objects.create(user=request.user, recipe=recipe)
            return Response({'detail': "Favourites created"}, status=201)

























