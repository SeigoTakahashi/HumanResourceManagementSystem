from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from accounts.models import CustomUser as User
from notification.models import Notification
from notification.utils import send_custom_email

LOGIN_URL = "http://127.0.0.1:8000/accounts/login/"

@receiver(user_logged_in)
def update_first_login_flag(sender, request, user, **kwargs):
    if isinstance(user, User) and user.is_first_login:
        message = f"初期パスワードを変更をお願いします。\nログインはこちら: {LOGIN_URL}"
        Notification.objects.create(user=request.user, message="初期パスワードを変更をお願いします。")
        send_custom_email(subject='初期パスワード変更のお願い', message=message, from_email=None, recipient_list=[request.user.email])
        user.is_first_login = False
        user.save()
