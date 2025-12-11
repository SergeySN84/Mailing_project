import os

import django
from django.conf import settings
from django.core.mail import send_mail

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()


print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)

send_mail(
    subject="Test",
    message="Test message",
    from_email="test@example.com",
    recipient_list=["user@example.com"],
)
print("OK")
