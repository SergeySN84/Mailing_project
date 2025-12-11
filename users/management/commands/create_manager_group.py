from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from mailings.models import Client, Mailing, Message


class Command(BaseCommand):
    help = "Создаёт группу 'Менеджеры' с необходимыми правами"

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="Менеджеры")

        models = [Mailing, Client, Message]
        all_permissions = []

        for model in models:
            ct = ContentType.objects.get_for_model(model)
            perms = Permission.objects.filter(content_type=ct)
            all_permissions.extend(perms)

        group.permissions.set(all_permissions)
        self.stdout.write(self.style.SUCCESS("Группа 'Менеджеры' успешно настроена."))
