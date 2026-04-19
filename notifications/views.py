from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from .models import Notification
from accounts.serializers import UserMinimalSerializer


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserMinimalSerializer(read_only=True)
    message = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notif_type', 'message', 'post', 'is_read', 'created_at']


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).select_related('sender')

    def get_serializer_context(self):
        return {'request': self.request}


class MarkReadView(APIView):
    def post(self, request, pk=None):
        if pk:
            Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
        else:
            Notification.objects.filter(recipient=request.user).update(is_read=True)
        return Response({'status': 'ok'})


class UnreadCountView(APIView):
    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return Response({'count': count})
