from django.urls import path
from .views import MessageListView, MessageCreateView, MessageMarkReadView

app_name = 'message'
urlpatterns = [
    path('', MessageListView.as_view(), name='message_list'),
    path('create/', MessageCreateView.as_view(), name='message_create'),
    path('mark_as_read/<int:message_id>/', MessageMarkReadView.as_view(), name='mark_as_read'),
]
