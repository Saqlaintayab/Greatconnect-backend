from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer

User = get_user_model()


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer

    def get_queryset(self):
        return self.request.user.conversations.prefetch_related('participants', 'messages')

    def get_serializer_context(self):
        return {'request': self.request}


class GetOrCreateConversationView(APIView):
    def post(self, request, user_id):
        other_user = User.objects.get(pk=user_id)
        # Find existing conversation between these two users
        conv = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, other_user)
        serializer = ConversationSerializer(conv, context={'request': request})
        return Response(serializer.data)


class MessageListView(generics.ListAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        conv_id = self.kwargs['conv_id']
        conv = Conversation.objects.get(pk=conv_id)
        if self.request.user not in conv.participants.all():
            return Message.objects.none()
        # Mark messages as read
        conv.messages.exclude(sender=self.request.user).update(is_read=True)
        return conv.messages.select_related('sender')

    def get_serializer_context(self):
        return {'request': self.request}


class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        conv = Conversation.objects.get(pk=self.kwargs['conv_id'])
        serializer.save(sender=self.request.user, conversation=conv)
        conv.save()

    def get_serializer_context(self):
        return {'request': self.request}
