import datetime
from datetime import timedelta
from django.contrib.auth.views import get_user_model
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from connectify.models import Rating
from .models import Recipes, Category, RecipesMedia
from .permissions import IsMainAdminOrReadOnly
from .serializers import (
    RecipesSerializer, CategoryQuerySerializer,
    MyRecipesSerializer, RecipesDetailSerializer,
    RecipeUpdateSerializer, RecipesFilterSerializer,
    QuerySerializer,
)

User = get_user_model()


class CategoryListAPIView(generics.GenericAPIView):
    serializer_class = RecipesSerializer
    permission_classes = [IsMainAdminOrReadOnly]

    @swagger_auto_schema(query_serializer=CategoryQuerySerializer())
    def get(self, request):
        query = request.GET.get('query')
        categories = Category.objects.get(pk=query)
        recipe_list = Recipes.objects.filter(category=categories)
        return Response(RecipesSerializer(recipe_list, many=True).data)


class RecipesListAPIView(generics.ListAPIView):
    queryset = Recipes.objects.all()
    serializer_class = RecipesSerializer


class MyRecipesListAPIView(generics.ListAPIView):
    serializer_class = MyRecipesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recipes.objects.filter(user=self.request.user)


class RecipeCreateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipesDetailSerializer

    def post(self, request):
        user = request.user
        media_files = request.data.get('media', [])

        if not media_files:
            return Response({'success': False, 'error': 'Media not found'}, status=400)

        try:
            category = Category.objects.get(pk=request.data['category'])
        except Category.DoesNotExist:
            return Response({'success': False, 'error': 'Category not found'}, status=404)
        new_recipe = Recipes.objects.create(
            user=user,
            category=category,
            recipe_name=request.data['recipe_name'],
            description=request.data['description']
        )
        for media in media_files:
            RecipesMedia.objects.create(
                recipe=new_recipe,
                media=media
            )
        serializer = RecipesSerializer(new_recipe)
        return Response({'success': True, 'detail': serializer.data}, status=201)



class RecipeUpdateAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipeUpdateSerializer
    queryset = Recipes.objects.all()

    def put(self, request, pk):
        user = request.user
        recipe_data = Recipes.objects.get(pk=pk, user=user)
        if recipe_data:
            recipe_data.recipe_name = request.data['recipe_name']
            recipe_data.description = request.data['description']
            recipe_data.save()
            recipe_serializer = MyRecipesSerializer(recipe_data).data
            return Response(recipe_serializer)


class RecipeDeleteAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MyRecipesSerializer
    queryset = Recipes.objects.all()

    def delete(self, request, pk):
        user = request.user
        try:
            recipe = Recipes.objects.get(pk=pk, user=user)
        except Recipes.DoesNotExist:
            return Response({'success': False, 'error': 'Recipe not found'})
        RecipesMedia.objects.filter(recipe=recipe).delete()
        recipe.delete()
        return Response({'success': True})


class RecipesFilterAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RecipesFilterSerializer

    @swagger_auto_schema(query_serializer=RecipesFilterSerializer())
    def get(self, request):
        time = request.GET.get('time')
        rate = request.GET.get('rating')
        category = request.GET.get('category', [])

        if rate:
            rate_query = Q(id__in=Rating.objects.filter(rating__lte=rate).values_list('recipe', flat=True))
        else:
            rate_query = Q()

        if not category:
            category_query = Q()
        else:
            category_ids = Category.objects.filter(name__icontains=category)
            category_query = Q(category__in=category_ids)

        q = category_query & rate_query
        recipes = Recipes.objects.filter(q)

        if time == 'new':
            recipes = recipes.filter(Q(created_at__gte=datetime.datetime.now() - timedelta(days=3)))
        elif time == 'oldest':
            recipes = recipes.order_by('created_at')
        elif time == 'popular':
            recipes = recipes.order_by('-popular')

        serializer = RecipesSerializer(recipes, many=True)
        return Response(serializer.data)


class SearchAPIView(generics.GenericAPIView):
    permission_classes = ()
    serializer_class = RecipesSerializer

    @swagger_auto_schema(query_serializer=QuerySerializer())
    def get(self, request):
        query = request.GET.get('query')
        base_categories = Recipes.objects.filter(Q(recipe_name__icontains=query))
        serializer = RecipesSerializer(base_categories, many=True)
        return Response({'success': True, 'categories': serializer.data})
