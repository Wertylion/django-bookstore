from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


GROUP_PERMISSIONS = {
    'customers': [
        'view_book',
        'add_rating',
        'change_rating',
        'view_rating',
    ],
    'managers': [
        'add_book',
        'change_book',
        'delete_book',
        'view_book',
        'add_author',
        'change_author',
        'view_author',
        'add_category',
        'change_category',
        'view_category',
        'add_publisher',
        'change_publisher',
        'view_publisher',
    ],
    'admins': [
        'add_book',
        'change_book',
        'delete_book',
        'view_book',
        'add_rating',
        'change_rating',
        'delete_rating',
        'view_rating',
        'add_author',
        'change_author',
        'delete_author',
        'view_author',
        'add_category',
        'change_category',
        'delete_category',
        'view_category',
        'add_publisher',
        'change_publisher',
        'delete_publisher',
        'view_publisher',
    ],
}


class Command(BaseCommand):
    help = 'Create default bookstore groups and attach model permissions.'

    def handle(self, *args, **options):
        for group_name, codenames in GROUP_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(name=group_name)
            permissions = Permission.objects.filter(codename__in=codenames)
            group.permissions.set(permissions)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Group "{group_name}" configured with {permissions.count()} permissions.'
                )
            )
