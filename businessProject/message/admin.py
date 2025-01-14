from django.contrib import admin
from .models import Message
from notification.models import Notification

class MessageAdmin(admin.ModelAdmin):
    pass

class NotificationAdmin(admin.ModelAdmin):
    pass
admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)

