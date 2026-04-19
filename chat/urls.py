from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListView.as_view()),
    path('conversations/<int:user_id>/get-or-create/', views.GetOrCreateConversationView.as_view()),
    path('conversations/<int:conv_id>/messages/', views.MessageListView.as_view()),
    path('conversations/<int:conv_id>/send/', views.SendMessageView.as_view()),
]
