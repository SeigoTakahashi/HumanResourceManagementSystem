from django.views.generic import ListView, CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from collections import defaultdict
from accounts.models import CustomUser
from .models import Message
from notification.utils import send_custom_email

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"

class MessageListView(LoginRequiredMixin, ListView):
    """ メッセージ一覧 """

    model = Message
    template_name = 'messages/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        # ログインユーザーが送信または受信したメッセージを取得
        return Message.objects.filter(
            recipient=self.request.user
        ).order_by('-timestamp')


class MessageCreateView(LoginRequiredMixin, CreateView):
    """ メッセージ作成 """

    model = Message
    template_name = 'messages/message_form.html'
    fields = ['recipient', 'content']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 入社日でユーザーをグループ化
        if self.request.user.is_staff:
            users = CustomUser.objects.filter(is_active=True, is_staff=False).order_by('date_of_joining')
        else:
            users = CustomUser.objects.filter(is_active=True, is_staff=True).order_by('date_of_joining')
        users_by_join_date = defaultdict(list)
        for user in users:
            join_date = user.date_of_joining if user.date_of_joining else '未設定'
            users_by_join_date[join_date].append(user)
        
        context['users_by_join_date'] = dict(users_by_join_date)
        return context
    
    def form_valid(self, form):
        form.instance.sender = self.request.user
        message = f"{self.request.user.first_name}さんから新しいメッセージが届きました。\n確認お願いします。\nログインはこちら: {LOGIN_URL}"
        send_custom_email(
            subject='新しいメッセージが届きました',
            message=message,
            from_email=None,
            recipient_list=[form.instance.recipient.email]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("message:message_list" )
        
class MessageMarkReadView(LoginRequiredMixin, View):
    @method_decorator(require_POST)
    def post(self, request, message_id):
        try:
            message = Message.objects.get(
                id=message_id, 
                recipient=request.user
            )
            message.is_read = True
            message.save()
            return JsonResponse({
                'status': 'success',
                'message_id': message_id
            })
        except Message.DoesNotExist:
            return JsonResponse({
                'status': 'error', 
                'message': '対象のメッセージが見つかりませんでした'
            }, status=404)