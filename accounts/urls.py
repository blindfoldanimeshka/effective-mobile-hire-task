from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r"business-elements", views.BusinessElementViewSet, basename="business-element")

urlpatterns = [
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("profile/", views.profile_view, name="profile"),
    path("admin/roles/", views.role_list_create_view, name="role-list-create"),
    path("admin/access-rules/", views.access_rule_list_create_view, name="access-rule-list-create"),
    path("admin/access-rules/<int:pk>/", views.access_rule_detail_view, name="access-rule-detail"),
    path("admin/users/<uuid:user_id>/role/", views.assign_role_view, name="assign-role"),
    path("", include(router.urls)),
]
