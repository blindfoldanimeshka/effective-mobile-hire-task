from rest_framework.permissions import BasePermission
from .models import UserRole, AccessRule


ACTION_TO_PERMISSION = {
    "list": "can_read",
    "retrieve": "can_read",
    "create": "can_create",
    "update": "can_update",
    "partial_update": "can_update",
    "destroy": "can_delete",
}


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return UserRole.objects.filter(
            user=request.user, role__name="admin"
        ).exists()


class HasAccessRule(BasePermission):
    def has_permission(self, request, view):
        action = request.method
        method_map = {
            "GET": "list",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "destroy",
        }
        action_name = method_map.get(action, action.lower())
        perm_field = ACTION_TO_PERMISSION.get(action_name)
        if not perm_field:
            return False

        if action_name == "list":
            return AccessRule.objects.filter(
                role__user_roles__user=request.user,
                can_read=True,
            ).exists()

        if action_name == "create":
            return AccessRule.objects.filter(
                role__user_roles__user=request.user,
                can_create=True,
            ).exists()

        return True

    def has_object_permission(self, request, view, obj):
        action = request.method
        method_map = {
            "GET": "retrieve",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "destroy",
        }
        action_name = method_map.get(action, action.lower())
        perm_field = ACTION_TO_PERMISSION.get(action_name)
        if not perm_field:
            return False

        has_perm = AccessRule.objects.filter(
            role__user_roles__user=request.user,
            business_element=obj,
            **{perm_field: True},
        ).exists()

        return has_perm
