from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('me/', views.MeView.as_view(), name='me'),
    path('search/', views.UserSearchView.as_view(), name='user_search'),
    path('suggested/', views.SuggestedUsersView.as_view(), name='suggested_users'),
    path('<str:username>/', views.UserProfileView.as_view(), name='user_profile'),
]
