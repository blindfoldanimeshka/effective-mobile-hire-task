from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Role, UserRole, BusinessElement, AccessRule

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "first_name", "last_name", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["email"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "created_at"]


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    list_display = ["role", "business_element", "can_read", "can_create", "can_update", "can_delete"]
