from django.db import models
from django.contrib.auth.views import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Recipes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    recipe_name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.recipe_name


class RecipesMedia(models.Model):
    recipe = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    media = models.FileField(upload_to='media/recipesmedia/')

