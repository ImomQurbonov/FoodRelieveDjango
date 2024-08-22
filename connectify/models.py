from django.db import models
from django.contrib.auth.views import get_user_model
from recipes.models import Recipes

User = get_user_model()

class Follow(models.Model):
    followers = models.ForeignKey(User,on_delete=models.CASCADE, related_name='follower')
    following = models.ForeignKey(User,on_delete=models.CASCADE, related_name='following')


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='recipe_ratings')
    rating = models.IntegerField()


class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='recipe_comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE, related_name='recipe_favorites')
