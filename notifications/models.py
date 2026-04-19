from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Liked your post'),
        ('comment', 'Commented on your post'),
        ('friend_request', 'Sent you a friend request'),
        ('friend_accept', 'Accepted your friend request'),
        ('follow', 'Started following you'),
        ('mention', 'Mentioned you'),
        ('story', 'Posted a story'),
    ]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications')
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.ForeignKey('posts.Comment', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} → {self.recipient}: {self.notif_type}'

    @property
    def message(self):
        msgs = {
            'like': f'{self.sender.full_name} liked your post',
            'comment': f'{self.sender.full_name} commented on your post',
            'friend_request': f'{self.sender.full_name} sent you a friend request',
            'friend_accept': f'{self.sender.full_name} accepted your friend request',
            'follow': f'{self.sender.full_name} started following you',
            'mention': f'{self.sender.full_name} mentioned you',
            'story': f'{self.sender.full_name} posted a new story',
        }
        return msgs.get(self.notif_type, 'New notification')
