from django.core.mail import send_mail

def send_custom_email(subject, message, from_email, recipient_list, html_message=None):
    """カスタムメール送信関数"""
    send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=html_message
    )