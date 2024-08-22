from django.db import models
from django.contrib.auth.views import get_user_model

User = get_user_model()


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.name


class ProfilesImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    image = models.ImageField(upload_to='media/profilesimage/')
