from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def create_notification(recipient, sender, notif_type, post=None, comment=None):
    if recipient == sender:
        return
    from .models import Notification
    notif = Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        post=post,
        comment=comment,
    )
    # Push via WebSocket
    channel_layer = get_channel_layer()
    try:
        async_to_sync(channel_layer.group_send)(
            f'notifications_{recipient.id}',
            {
                'type': 'send_notification',
                'notification': {
                    'id': notif.id,
                    'type': notif_type,
                    'message': notif.message,
                    'sender': {
                        'id': sender.id,
                        'username': sender.username,
                        'full_name': sender.full_name,
                        'avatar_url': sender.avatar_url,
                    },
                    'post_id': post.id if post else None,
                    'is_read': False,
                    'created_at': notif.created_at.isoformat(),
                }
            }
        )
    except Exception:
        pass
    return notif
