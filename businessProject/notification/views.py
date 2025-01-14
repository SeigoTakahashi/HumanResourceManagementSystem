from django.views.generic import TemplateView, View
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from request.views import UnsubmittedListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from .utils import send_custom_email

class NotificationDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "notification/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['unread_notifications'] = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
        context['read_notifications'] = Notification.objects.filter(user=user, is_read=True).order_by('-created_at')
        return context

class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return redirect('notification:dashboard')


class SendReminderView(LoginRequiredMixin, View):
    """未提出の内定者にリマインダーメールを送信"""

    @method_decorator(staff_member_required)
    def post(self, request):
        # UnsubmittedListViewのインスタンスを作成し、requestを設定
        unsubmitted_view = UnsubmittedListView()
        unsubmitted_view.request = request
        # get_querysetを呼び出し
        unsubmitted_users = unsubmitted_view.get_queryset()
        # メール送信
        for user in unsubmitted_users:
            # メールの詳細をカスタマイズ
            subject = '【重要】入社前書類提出のリマインダー'
            message = f'''
            {user.first_name} 様

            入社日まで残りわずかです。以下の書類を至急提出してください：
            1. 住居・身上確認書
            {' 2. 自転車通勤申請書' if user.confirmation_set.filter(is_bicycle_commute=True).exists() else ''}

            ご不明な点は人事部までお問い合わせください。
            '''
            
            send_custom_email(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[user.email],
            )

        return JsonResponse({
            'status': 'success', 
            'message': f'{len(unsubmitted_users)}件のリマインダーを送信しました'
        })