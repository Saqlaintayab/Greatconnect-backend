from django.urls import path
from . import views

urlpatterns = [
    path('', views.StoryFeedView.as_view()),
    path('create/', views.StoryCreateView.as_view()),
    path('<int:pk>/view/', views.StoryViewView.as_view()),
    path('<int:pk>/delete/', views.StoryDeleteView.as_view()),
]
