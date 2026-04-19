from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.FeedView.as_view(), name='feed'),
    path('create/', views.PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/like/', views.LikePostView.as_view(), name='post_like'),
    path('<int:pk>/comments/', views.CommentListCreateView.as_view(), name='post_comments'),
    path('user/<str:username>/', views.UserPostsView.as_view(), name='user_posts'),
]
