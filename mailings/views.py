from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from .forms import ClientForm, MailingForm, MessageForm
from .models import Client, Message, Mailing, MailingAttempt
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailings/mailing_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджеры").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")
    template_name = "mailings/mailing_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailings:mailing_list")
    template_name = "mailings/mailing_form.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            obj.owner != self.request.user
            and not self.request.user.groups.filter(name="Менеджеры").exists()
        ):
            raise PermissionDenied("Вы не можете редактировать чужую рассылку.")
        return obj


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy("mailings:mailing_list")
    template_name = "mailings/mailing_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужую рассылку.")
        return obj


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailings/mailing_detail.html"
    context_object_name = "mailing"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        return obj


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "mailings/client_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджеры").exists():
            return Client.objects.all()
        return Client.objects.filter(owner=user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")
    template_name = "mailings/client_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy("mailings:client_list")
    template_name = "mailings/client_form.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            obj.owner != self.request.user
            and not self.request.user.groups.filter(name="Менеджеры").exists()
        ):
            raise PermissionDenied("Вы не можете редактировать чужого клиента.")
        return obj


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy("mailings:client_list")
    template_name = "mailings/client_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужого клиента.")
        return obj


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailings/message_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджеры").exists():
            return Message.objects.all()
        return Message.objects.filter(owner=user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")
    template_name = "mailings/message_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy("mailings:message_list")
    template_name = "mailings/message_form.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if (
            obj.owner != self.request.user
            and not self.request.user.groups.filter(name="Менеджеры").exists()
        ):
            raise PermissionDenied("Вы не можете редактировать чужое сообщение.")
        return obj


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy("mailings:message_list")
    template_name = "mailings/message_confirm_delete.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise PermissionDenied("Вы не можете удалить чужое сообщение.")
        return obj


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = "mailings/attempt_list.html"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Менеджеры").exists():
            return MailingAttempt.objects.select_related("mailing").all()
        return MailingAttempt.objects.filter(mailing__owner=user).select_related(
            "mailing"
        )


@login_required
def home(request):
    total_mailings = Mailing.objects.count()
    active_mailings = Mailing.objects.filter(
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now(),
    ).count()
    unique_clients = Client.objects.count()

    return render(
        request,
        "home.html",
        {
            "total_mailings": total_mailings,
            "active_mailings": active_mailings,
            "unique_clients": unique_clients,
        },
    )


@login_required
def send_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    now = timezone.now()
    if mailing.start_time > now or mailing.end_time < now:
        messages.error(
            request,
            "Рассылка не может быть отправлена: текущее время вне диапазона отправки.",
        )
        return redirect("mailings:mailing_list")

    if mailing.get_status() != "Запущена":
        messages.error(request, "Рассылка неактивна.")
        return redirect("mailings:mailing_list")

    success_count = 0
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
            success_count += 1
        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                status="Не успешно",
                server_response=str(e),
            )

    messages.success(
        request,
        f"Рассылка отправлена! Успешно: {success_count} из {mailing.clients.count()}.",
    )
    return redirect("mailings:mailing_list")
