from django.core.management.base import BaseCommand
from accounts.models import User, Role, UserRole, BusinessElement, AccessRule


class Command(BaseCommand):
    help = "Seed database with initial data"

    def handle(self, *args, **options):
        admin_role, _ = Role.objects.get_or_create(name="admin", defaults={"description": "Full access administrator"})
        manager_role, _ = Role.objects.get_or_create(name="manager", defaults={"description": "Manager with limited write access"})
        viewer_role, _ = Role.objects.get_or_create(name="viewer", defaults={"description": "Read-only access"})

        article, _ = BusinessElement.objects.get_or_create(name="article", defaults={"description": "News articles"})
        product, _ = BusinessElement.objects.get_or_create(name="product", defaults={"description": "Product catalog"})
        order, _ = BusinessElement.objects.get_or_create(name="order", defaults={"description": "Customer orders"})

        for element in [article, product, order]:
            AccessRule.objects.get_or_create(
                role=admin_role, business_element=element,
                defaults={"can_read": True, "can_create": True, "can_update": True, "can_delete": True},
            )

        for element in [article, product, order]:
            AccessRule.objects.get_or_create(
                role=manager_role, business_element=element,
                defaults={"can_read": True, "can_create": True, "can_update": True, "can_delete": False},
            )

        for element in [article, product, order]:
            AccessRule.objects.get_or_create(
                role=viewer_role, business_element=element,
                defaults={"can_read": True, "can_create": False, "can_update": False, "can_delete": False},
            )

        admin_user, created = User.objects.get_or_create(
            email="admin@example.com",
            defaults={"first_name": "Admin", "last_name": "User", "is_staff": True},
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
        UserRole.objects.get_or_create(user=admin_user, role=admin_role)

        manager_user, created = User.objects.get_or_create(
            email="manager@example.com",
            defaults={"first_name": "Manager", "last_name": "User"},
        )
        if created:
            manager_user.set_password("manager123")
            manager_user.save()
        UserRole.objects.get_or_create(user=manager_user, role=manager_role)

        viewer_user, created = User.objects.get_or_create(
            email="viewer@example.com",
            defaults={"first_name": "Viewer", "last_name": "User"},
        )
        if created:
            viewer_user.set_password("viewer123")
            viewer_user.save()
        UserRole.objects.get_or_create(user=viewer_user, role=viewer_role)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
