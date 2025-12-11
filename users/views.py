import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import CreateView, UpdateView

from .forms import UserProfileForm, UserRegisterForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.verification_token = secrets.token_urlsafe(32)
        user.token_created_at = timezone.now()
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = user.verification_token
        activation_url = self.request.build_absolute_uri(
            reverse_lazy("users:verify_email", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            subject="Подтвердите ваш email",
            message=f"Перейдите по ссылке для подтверждения: {activation_url}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Регистрация прошла успешно! Проверьте email для подтверждения.",
        )
        return super().form_valid(form)


def verify_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and user.verification_token == token:
        token_age = timezone.now() - user.token_created_at
        if token_age < timedelta(hours=1):
            user.is_active = True
            user.verification_token = None
            user.token_created_at = None
            user.save()
            messages.success(request, "Ваш email подтверждён! Теперь вы можете войти.")
            return redirect("users:login")
        else:
            messages.error(
                request, "Срок действия ссылки истёк. Зарегистрируйтесь снова."
            )
    else:
        messages.error(request, "Неверная ссылка подтверждения.")

    return redirect("users:register")


class CustomLoginView(LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("users:login")
    template_name = "users/login.html"
    http_method_names = ["get", "post", "options"]


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordResetView(PasswordResetView):
    template_name = "users/password_reset_form.html"
    email_template_name = "users/password_reset_email.html"
    success_url = reverse_lazy("users:password_reset_done")
    from_email = settings.EMAIL_HOST_USER


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password_reset_done.html"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "users/password_reset_confirm.html"
    success_url = reverse_lazy("users:password_reset_complete")


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "users/password_reset_complete.html"
