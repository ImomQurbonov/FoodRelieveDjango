from rest_framework import serializers
from django.contrib.auth.views import get_user_model
from rest_framework.exceptions import ValidationError

from connectify.models import Comments, Rating, Favorite

User = get_user_model()


class FollowListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class FollowSerializer(serializers.Serializer):
    following = serializers.IntegerField()


class FavouriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ['recipe']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('rating', 'recipe')

        def validate_rating(self, value):
            if value < 1 or value > 5:
                raise ValidationError("Rating must be between 1 and 5.")
            return value


class ReviewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = ('recipe', 'comment')