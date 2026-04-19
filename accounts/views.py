from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserProfileSerializer, UpdateProfileSerializer, UserMinimalSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserProfileSerializer(user, context={'request': request}).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'})
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateProfileSerializer
        return UserProfileSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

    def get_serializer_context(self):
        return {'request': self.request}


class UserSearchView(generics.ListAPIView):
    serializer_class = UserMinimalSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if not query:
            return User.objects.none()
        return User.objects.filter(
            username__icontains=query
        ).exclude(id=self.request.user.id) | User.objects.filter(
            first_name__icontains=query
        ).exclude(id=self.request.user.id) | User.objects.filter(
            last_name__icontains=query
        ).exclude(id=self.request.user.id)

    def get_serializer_context(self):
        return {'request': self.request}


class SuggestedUsersView(generics.ListAPIView):
    serializer_class = UserMinimalSerializer

    def get_queryset(self):
        from friends.models import Friendship, FriendRequest
        user = self.request.user
        friend_ids = list(Friendship.objects.filter(
            user1=user
        ).values_list('user2_id', flat=True)) + list(
            Friendship.objects.filter(user2=user).values_list('user1_id', flat=True)
        )
        pending_ids = list(FriendRequest.objects.filter(
            sender=user, status='pending'
        ).values_list('receiver_id', flat=True))
        exclude_ids = friend_ids + pending_ids + [user.id]
        return User.objects.exclude(id__in=exclude_ids).order_by('?')[:10]

    def get_serializer_context(self):
        return {'request': self.request}
