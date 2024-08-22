from django.contrib import admin
from authmanager.models import UserRole, Role


admin.site.register((UserRole, Role))
