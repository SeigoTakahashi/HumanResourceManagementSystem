from .models import Notification
from message.models import Message

def unread_notifications_count(request):
    if request.user.is_authenticated:  
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        message_count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_notifications_count': unread_count, 'unread_messages_count': message_count}
    return {'unread_notifications_count': 0}