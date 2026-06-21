from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from accounts.models import Role, UserRole, BusinessElement, AccessRule

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_role = Role.objects.create(name="admin", description="Admin role")
        self.viewer_role = Role.objects.create(name="viewer", description="Viewer role")

        self.article = BusinessElement.objects.create(name="article", description="Articles")

        AccessRule.objects.create(
            role=self.admin_role, business_element=self.article,
            can_read=True, can_create=True, can_update=True, can_delete=True,
        )
        AccessRule.objects.create(
            role=self.viewer_role, business_element=self.article,
            can_read=True, can_create=False, can_update=False, can_delete=False,
        )

        self.admin_user = User.objects.create_user(
            email="admin@test.com", password="admin123",
            first_name="Admin", last_name="Test",
        )
        UserRole.objects.create(user=self.admin_user, role=self.admin_role)

        self.viewer_user = User.objects.create_user(
            email="viewer@test.com", password="viewer123",
            first_name="Viewer", last_name="Test",
        )
        UserRole.objects.create(user=self.viewer_user, role=self.viewer_role)

        self.inactive_user = User.objects.create_user(
            email="inactive@test.com", password="inactive123",
            first_name="Inactive", last_name="Test",
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def get_tokens(self, email, password):
        response = self.client.post("/api/auth/login/", {"email": email, "password": password})
        if response.status_code == 200:
            return response.data["access"]
        return None

    def auth(self, email, password):
        token = self.get_tokens(email, password)
        if token:
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class RegistrationTests(BaseTestCase):

    def test_register_success(self):
        response = self.client.post("/api/auth/register/", {
            "email": "new@test.com",
            "first_name": "New",
            "last_name": "User",
            "password": "pass123",
            "password_confirm": "pass123",
        })
        self.assertEqual(response.status_code, 201)

    def test_register_duplicate_email(self):
        response = self.client.post("/api/auth/register/", {
            "email": "admin@test.com",
            "first_name": "Dup",
            "last_name": "User",
            "password": "pass123",
            "password_confirm": "pass123",
        })
        self.assertEqual(response.status_code, 400)

    def test_register_password_mismatch(self):
        response = self.client.post("/api/auth/register/", {
            "email": "mismatch@test.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "pass123",
            "password_confirm": "pass456",
        })
        self.assertEqual(response.status_code, 400)

    def test_register_missing_fields(self):
        response = self.client.post("/api/auth/register/", {"email": "x@test.com"})
        self.assertEqual(response.status_code, 400)


class LoginTests(BaseTestCase):

    def test_login_success(self):
        response = self.client.post("/api/auth/login/", {
            "email": "admin@test.com", "password": "admin123",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_wrong_password(self):
        response = self.client.post("/api/auth/login/", {
            "email": "admin@test.com", "password": "wrong",
        })
        self.assertEqual(response.status_code, 401)

    def test_login_nonexistent_user(self):
        response = self.client.post("/api/auth/login/", {
            "email": "noone@test.com", "password": "pass",
        })
        self.assertEqual(response.status_code, 401)

    def test_login_inactive_user(self):
        response = self.client.post("/api/auth/login/", {
            "email": "inactive@test.com", "password": "inactive123",
        })
        self.assertEqual(response.status_code, 401)


class ProfileTests(BaseTestCase):

    def test_get_profile(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "admin@test.com")

    def test_update_profile(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.patch("/api/profile/", {"first_name": "Updated"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Updated")

    def test_profile_no_token(self):
        response = self.client.get("/api/profile/")
        self.assertEqual(response.status_code, 401)

    def test_soft_delete(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.delete("/api/profile/")
        self.assertEqual(response.status_code, 200)
        self.admin_user.refresh_from_db()
        self.assertFalse(self.admin_user.is_active)

    def test_deleted_user_cannot_login(self):
        self.auth("inactive@test.com", "inactive123")
        response = self.client.delete("/api/profile/")
        response = self.client.post("/api/auth/login/", {
            "email": "inactive@test.com", "password": "inactive123",
        })
        self.assertEqual(response.status_code, 401)


class AccessControlTests(BaseTestCase):

    def test_list_elements_with_read(self):
        self.auth("viewer@test.com", "viewer123")
        response = self.client.get("/api/business-elements/")
        self.assertEqual(response.status_code, 200)

    def test_list_elements_without_read(self):
        no_role_user = User.objects.create_user(
            email="norole@test.com", password="pass123",
            first_name="No", last_name="Role",
        )
        token = self.get_tokens("norole@test.com", "pass123")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/business-elements/")
        self.assertEqual(response.status_code, 403)

    def test_create_element_with_permission(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.post("/api/business-elements/", {
            "name": "new_element", "description": "New"
        })
        self.assertEqual(response.status_code, 201)

    def test_create_element_without_permission(self):
        self.auth("viewer@test.com", "viewer123")
        response = self.client.post("/api/business-elements/", {
            "name": "new_element", "description": "New"
        })
        self.assertEqual(response.status_code, 403)

    def test_access_no_token(self):
        response = self.client.get("/api/business-elements/")
        self.assertEqual(response.status_code, 401)

    def test_delete_element_with_permission(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.delete(f"/api/business-elements/{self.article.pk}/")
        self.assertEqual(response.status_code, 204)

    def test_delete_element_without_permission(self):
        self.auth("viewer@test.com", "viewer123")
        response = self.client.delete(f"/api/business-elements/{self.article.pk}/")
        self.assertEqual(response.status_code, 403)


class AdminTests(BaseTestCase):

    def test_admin_list_roles(self):
        self.auth("admin@test.com", "admin123")
        response = self.client.get("/api/admin/roles/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_non_admin_list_roles(self):
        self.auth("viewer@test.com", "viewer123")
        response = self.client.get("/api/admin/roles/")
        self.assertEqual(response.status_code, 403)

    def test_admin_create_access_rule(self):
        self.auth("admin@test.com", "admin123")
        new_role = Role.objects.create(name="editor")
        response = self.client.post("/api/admin/access-rules/", {
            "role": new_role.pk,
            "business_element": self.article.pk,
            "can_read": True,
        })
        self.assertEqual(response.status_code, 201)

    def test_admin_assign_role(self):
        self.auth("admin@test.com", "admin123")
        new_user = User.objects.create_user(
            email="assign@test.com", password="pass123",
            first_name="Assign", last_name="Test",
        )
        response = self.client.post(f"/api/admin/users/{new_user.pk}/role/", {
            "role_id": self.viewer_role.pk,
        })
        self.assertEqual(response.status_code, 201)
