from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import FriendRequest, Friendship, Follow
from accounts.serializers import UserMinimalSerializer
from notifications.utils import create_notification

User = get_user_model()


class SendFriendRequestView(APIView):
    def post(self, request, user_id):
        receiver = User.objects.get(pk=user_id)
        if receiver == request.user:
            return Response({'error': 'Cannot add yourself.'}, status=400)
        req, created = FriendRequest.objects.get_or_create(
            sender=request.user, receiver=receiver
        )
        if created:
            create_notification(recipient=receiver, sender=request.user, notif_type='friend_request')
        return Response({'status': 'sent'})


class RespondFriendRequestView(APIView):
    def post(self, request, request_id):
        action = request.data.get('action')  # 'accept' or 'reject'
        try:
            freq = FriendRequest.objects.get(pk=request_id, receiver=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Not found.'}, status=404)

        if action == 'accept':
            freq.status = 'accepted'
            freq.save()
            # Create friendship (ensure user1 < user2 to avoid duplicates)
            u1, u2 = sorted([freq.sender, freq.receiver], key=lambda u: u.id)
            Friendship.objects.get_or_create(user1=u1, user2=u2)
            create_notification(recipient=freq.sender, sender=request.user, notif_type='friend_accept')
            return Response({'status': 'accepted'})
        elif action == 'reject':
            freq.status = 'rejected'
            freq.save()
            return Response({'status': 'rejected'})
        return Response({'error': 'Invalid action.'}, status=400)


class UnfriendView(APIView):
    def delete(self, request, user_id):
        other = User.objects.get(pk=user_id)
        Friendship.objects.filter(
            user1__in=[request.user, other], user2__in=[request.user, other]
        ).delete()
        FriendRequest.objects.filter(
            sender__in=[request.user, other], receiver__in=[request.user, other]
        ).delete()
        return Response({'status': 'unfriended'})


class FriendListView(generics.ListAPIView):
    serializer_class = UserMinimalSerializer

    def get_queryset(self):
        user = self.request.user
        friend_ids = list(Friendship.objects.filter(user1=user).values_list('user2_id', flat=True)) + \
                     list(Friendship.objects.filter(user2=user).values_list('user1_id', flat=True))
        return User.objects.filter(id__in=friend_ids)

    def get_serializer_context(self):
        return {'request': self.request}


class PendingRequestsView(generics.ListAPIView):
    serializer_class = UserMinimalSerializer

    def get_queryset(self):
        requests = FriendRequest.objects.filter(receiver=self.request.user, status='pending')
        return [r.sender for r in requests]

    def list(self, request, *args, **kwargs):
        reqs = FriendRequest.objects.filter(receiver=request.user, status='pending')
        data = []
        for r in reqs:
            data.append({
                'request_id': r.id,
                'sender': UserMinimalSerializer(r.sender, context={'request': request}).data,
                'created_at': r.created_at,
            })
        return Response(data)


class FollowView(APIView):
    def post(self, request, user_id):
        user_to_follow = User.objects.get(pk=user_id)
        follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
        if created:
            create_notification(recipient=user_to_follow, sender=request.user, notif_type='follow')
        return Response({'status': 'following'})

    def delete(self, request, user_id):
        user_to_unfollow = User.objects.get(pk=user_id)
        Follow.objects.filter(follower=request.user, following=user_to_unfollow).delete()
        return Response({'status': 'unfollowed'})
