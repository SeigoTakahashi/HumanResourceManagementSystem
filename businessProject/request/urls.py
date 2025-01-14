from django.urls import path
from .views import (ConfirmationView, 
                    BicycleCommuteView, 
                    PendingListView, 
                    ConfirmationDetailView, 
                    BicycleCommuteDetailView, 
                    RejectingListView, 
                    ApprovedListView, 
                    UnprocessingListView, 
                    ConfirmationUpdateView, 
                    BicycleCommuteUpdateView,
                    UnsubmittedListView)

app_name = 'request'
urlpatterns = [
    path('confirmation/', ConfirmationView.as_view(), name='confirmation'),  
    path('bicycle_commute/', BicycleCommuteView.as_view(), name='bicycle_commute'),
    path('pending_list/', PendingListView.as_view(), name='pending_list'),
    path('rejecting_list/', RejectingListView.as_view(), name='rejecting_list'),
    path('approving_list/', ApprovedListView.as_view(), name='approving_list'),
    path('unprocessing_list/', UnprocessingListView.as_view(), name='unprocessing_list'),
    path('detail_confirmation/<int:pk>/', ConfirmationDetailView.as_view(), name='detail_confirmation'),
    path('detail_bicycle_commute/<int:pk>/', BicycleCommuteDetailView.as_view(), name='detail_bicycle_commute'),
    path('update_confirmation/<int:pk>/', ConfirmationUpdateView.as_view(), name='update_confirmation'),
    path('update_bicycle_commute/<int:pk>/', BicycleCommuteUpdateView.as_view(), name='update_bicycle_commute'),
    path('unsubmitted_list', UnsubmittedListView.as_view(), name='unsubmitted_list'),
]