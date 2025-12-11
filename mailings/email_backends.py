from django.core.mail.backends.console import \
    EmailBackend as BaseConsoleEmailBackend
from django.core.mail.backends.dummy import \
    EmailBackend as BaseDummyEmailBackend
from django.core.mail.backends.locmem import \
    EmailBackend as BaseLocMemEmailBackend


class SafeConsoleEmailBackend(BaseConsoleEmailBackend):
    def check(self, **kwargs):
        return []


class SafeLocMemEmailBackend(BaseLocMemEmailBackend):
    def check(self, **kwargs):
        return []


class SafeDummyEmailBackend(BaseDummyEmailBackend):
    def check(self, **kwargs):
        return []
