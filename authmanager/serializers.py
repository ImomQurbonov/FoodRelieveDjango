from rest_framework import serializers
from django.contrib.auth.views import get_user_model
from authmanager.models import ProfilesImage
from connectify.models import Follow
from recipes.models import Recipes

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField()
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password', 'password_confirm')

    def create(self, validated_data):
        if validated_data['password'] == validated_data['password_confirm']:
            if User.objects.filter(email=validated_data['email']).exists():
                raise serializers.ValidationError('Email already exists!')
            if User.objects.filter(username=validated_data['username']).exists():
                raise serializers.ValidationError('Username already exists!')
            validated_data.pop('password_confirm')
            user = User.objects.create_user(**validated_data)
            return user
        else:
            raise serializers.ValidationError('Password are not found!')


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(max_length=20)


class GoogleRedirectSerializer(serializers.Serializer):
    google_redirect_uri = serializers.CharField(required=True)


class FacebookRedirectSerializer(serializers.Serializer):
    facebook_redirect_uri = serializers.CharField(required=True)
    facebook_app_id = serializers.CharField(required=True)


class UserProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProfilesImage
        fields = ['image']


class ProfileViewSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    recipe_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name',
                  'username', 'image',
                  'followers', 'following',
                  'recipe_count'
        )

    def get_image(self, obj):
        profile_image = ProfilesImage.objects.filter(user=obj).first()
        if profile_image:
            return profile_image.image.url
        return None

    def get_followers(self, obj):
        followers =  Follow.objects.filter(followers=obj)
        if followers:
            return followers.count()
        return None

    def get_following(self, obj):
        following = Follow.objects.filter(following=obj)
        if following:
            return following.count()
        return None

    def get_recipe_count(self, obj):
        recipe_count = Recipes.objects.filter(user=obj)
        if recipe_count:
            return recipe_count.count()
        return None



# Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI0MzcwNDc3LCJpYXQiOjE3MjQzMTA0NzcsImp0aSI6IjY4MTU5MmE4NGY5ZDRiODNiMTQwYzRkZThhYzAwOWE0IiwidXNlcl9pZCI6Mn0.4chvXVOsPNrwEkvPq0RdfNtCYuZu5TFOXIDgbcpAqXE






















