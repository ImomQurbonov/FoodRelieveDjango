from django.db.models import Avg
from rest_framework import serializers
from .models import Recipes, RecipesMedia, Category
from authmanager.models import ProfilesImage
from connectify.models import Rating, Comments


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['rating']


class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ['comment']


class ProfilesImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilesImage
        fields = ['image']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class RecipesMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipesMedia
        fields = ['media']


class RecipesSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    media = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    user_firstname = serializers.SerializerMethodField()
    user_lastname = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = [
            'id', 'user', 'recipe_name', 'description', 'created_at',
            'category', 'media', 'user_firstname',
            'user_lastname', 'user_image', 'average_rating'
        ]

    def get_media(self, obj):
        media_qs = RecipesMedia.objects.filter(recipe=obj)
        serializer = RecipesMediaSerializer(media_qs, many=True)
        return serializer.data

    def get_average_rating(self, obj):
        average_rating = Rating.objects.filter(recipe=obj).aggregate(average=Avg('rating'))['average']
        return average_rating if average_rating is not None else 0

    def get_user_firstname(self, obj):
        return obj.user.first_name

    def get_user_lastname(self, obj):
        return obj.user.last_name

    def get_user_image(self, obj):  # Method name updated to match the field name
        profile_image = obj.user.profilesimage_set.first()
        if profile_image:
            return ProfilesImageSerializer(profile_image).data
        return None


class MyRecipesSerializer(RecipesSerializer):
    category = CategorySerializer()
    media = serializers.SerializerMethodField()

    class Meta:
        model = Recipes
        fields = ['id', 'category', 'recipe_name',
                  'description', 'created_at',
                  'media']

        def get_media(self, obj):
            media_qs = RecipesMedia.objects.filter(recipe=obj)
            serializer = RecipesMediaSerializer(media_qs, many=True)
            return serializer.data


class RecipesDetailSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField()
    media = serializers.ListField(child=serializers.FileField(), write_only=True)
    class Meta:
        model = Recipes
        fields = ['category', 'recipe_name', 'description', 'media',]


class RecipeUpdateSerializer(RecipesSerializer):

    class Meta:
        model = Recipes
        fields = ['recipe_name', 'description']


class RecipesFilterSerializer(serializers.Serializer):
    time = serializers.CharField(required=False)
    rating = serializers.IntegerField(required=False)
    category = serializers.ListField(child=serializers.CharField(), required=False)


class QuerySerializer(serializers.Serializer):
    query = serializers.CharField()


class CategoryQuerySerializer(serializers.Serializer):
    query = serializers.IntegerField