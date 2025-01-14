from django.urls import path
from .views import SettingsHomeView, PasswordChangeDoneView, PasswordChangeSettingsView, EmailChange, EmailChangeDone, EmailChangeComplete

app_name = 'settings'

urlpatterns = [
    path('', SettingsHomeView.as_view(), name='settings_home'),
    path('passwordchange/', PasswordChangeSettingsView.as_view(), name='settings_passwordchange'),
    path('password_change/done/', PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('email/change/', EmailChange.as_view(), name='email_change'),
    path('email/change/done/', EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', EmailChangeComplete.as_view(), name='email_change_complete'),
]