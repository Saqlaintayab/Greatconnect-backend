from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.FriendListView.as_view()),
    path('requests/pending/', views.PendingRequestsView.as_view()),
    path('request/<int:user_id>/', views.SendFriendRequestView.as_view()),
    path('request/<int:request_id>/respond/', views.RespondFriendRequestView.as_view()),
    path('unfriend/<int:user_id>/', views.UnfriendView.as_view()),
    path('follow/<int:user_id>/', views.FollowView.as_view()),
]
