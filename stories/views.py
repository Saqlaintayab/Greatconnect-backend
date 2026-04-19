from rest_framework import serializers, generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Story, StoryView
from accounts.serializers import UserMinimalSerializer


class StorySerializer(serializers.ModelSerializer):
    author = UserMinimalSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    has_viewed = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'author', 'image_url', 'image', 'caption', 'views_count', 'has_viewed', 'created_at', 'expires_at']
        extra_kwargs = {'image': {'write_only': True}}

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_views_count(self, obj):
        return obj.views.count()

    def get_has_viewed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.views.filter(viewer=request.user).exists()
        return False


class StoryFeedView(generics.ListAPIView):
    serializer_class = StorySerializer

    def get_queryset(self):
        from friends.models import Friendship
        user = self.request.user
        friend_ids = list(Friendship.objects.filter(user1=user).values_list('user2_id', flat=True)) + \
                     list(Friendship.objects.filter(user2=user).values_list('user1_id', flat=True))
        friend_ids.append(user.id)
        return Story.objects.filter(author_id__in=friend_ids, expires_at__gt=timezone.now())

    def get_serializer_context(self):
        return {'request': self.request}


class StoryCreateView(generics.CreateAPIView):
    serializer_class = StorySerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class StoryViewView(APIView):
    def post(self, request, pk):
        story = Story.objects.get(pk=pk)
        StoryView.objects.get_or_create(story=story, viewer=request.user)
        return Response({'status': 'viewed'})


class StoryDeleteView(generics.DestroyAPIView):
    queryset = Story.objects.all()

    def destroy(self, request, *args, **kwargs):
        story = self.get_object()
        if story.author != request.user:
            return Response({'error': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        story.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
