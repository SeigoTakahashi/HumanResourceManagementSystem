from django.urls import path
from .views import NotificationDashboardView, MarkAsReadView, SendReminderView
	

app_name = 'notification'
urlpatterns = [
    path('dashboard/', NotificationDashboardView.as_view(), name='dashboard'),
    path('mark_as_read/<int:notification_id>/', MarkAsReadView.as_view(), name='mark_as_read'),
    path('send-reminders/', SendReminderView.as_view(), name='send_reminders'),
]