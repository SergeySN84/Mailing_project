from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailings.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = "Отправка активных рассылок в указанный период"

    def handle(self, *args, **options):
        now = timezone.now()
        mailings = Mailing.objects.filter(start_time__lte=now, end_time__gte=now)

        if not mailings:
            self.stdout.write("Нет активных рассылок для отправки.")
            return

        for mailing in mailings:
            self.stdout.write(f"Обработка рассылки ID={mailing.id}...")
            for client in mailing.clients.all():
                try:
                    send_mail(
                        subject=mailing.message.subject,
                        message=mailing.message.body,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[client.email],
                        fail_silently=False,
                    )
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="Успешно",
                        server_response="OK",
                    )
                    self.stdout.write(f"  → Успешно отправлено на {client.email}")
                except Exception as e:
                    MailingAttempt.objects.create(
                        mailing=mailing,
                        status="Не успешно",
                        server_response=str(e),
                    )
                    self.stderr.write(f"  → Ошибка при отправке на {client.email}: {e}")

        self.stdout.write(self.style.SUCCESS("Отправка рассылок завершена."))
