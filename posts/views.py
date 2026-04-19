from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .models import Post, Like, Comment
from .serializers import PostSerializer, LikeSerializer, CommentSerializer
from notifications.utils import create_notification

User = get_user_model()


class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        from friends.models import Friendship
        user = self.request.user
        friend_ids = list(Friendship.objects.filter(
            user1=user
        ).values_list('user2_id', flat=True)) + list(
            Friendship.objects.filter(user2=user).values_list('user1_id', flat=True)
        )
        friend_ids.append(user.id)
        return Post.objects.filter(
            author_id__in=friend_ids, privacy__in=['public', 'friends']
        ).select_related('author').prefetch_related('likes', 'comments')

    def get_serializer_context(self):
        return {'request': self.request}


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user:
            return Response({'error': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        username = self.kwargs['username']
        user = User.objects.get(username=username)
        if self.request.user == user:
            return Post.objects.filter(author=user)
        return Post.objects.filter(author=user, privacy='public')

    def get_serializer_context(self):
        return {'request': self.request}


class LikePostView(APIView):
    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        reaction = request.data.get('reaction', 'like')
        like, created = Like.objects.update_or_create(
            user=request.user, post=post,
            defaults={'reaction': reaction}
        )
        if created and post.author != request.user:
            create_notification(
                recipient=post.author,
                sender=request.user,
                notif_type='like',
                post=post,
            )
        return Response({'reaction': like.reaction, 'likes_count': post.likes_count})

    def delete(self, request, pk):
        post = Post.objects.get(pk=pk)
        Like.objects.filter(user=request.user, post=post).delete()
        return Response({'likes_count': post.likes_count})


class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['pk'], parent=None)

    def perform_create(self, serializer):
        post = Post.objects.get(pk=self.kwargs['pk'])
        comment = serializer.save(author=self.request.user, post=post)
        if post.author != self.request.user:
            create_notification(
                recipient=post.author,
                sender=self.request.user,
                notif_type='comment',
                post=post,
                comment=comment,
            )

    def get_serializer_context(self):
        return {'request': self.request}
