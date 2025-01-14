from django.contrib import admin
from django.urls import path, include
from request.views import DashboardView, RouteView

urlpatterns = [
    path('', RouteView.as_view(), name='route'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('route/', RouteView.as_view(), name='route'),
    path('request/', include('request.urls')),
    path('accounts/', include('accounts.urls')),
    path('settings/', include('settings.urls')),
    path('notification/', include('notification.urls')),
    path('message/', include('message.urls')),
    path("admin/", admin.site.urls),
]
