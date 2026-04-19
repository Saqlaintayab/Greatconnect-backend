from django.contrib import admin
from .models import FriendRequest, Friendship, Follow
admin.site.register(FriendRequest)
admin.site.register(Friendship)
admin.site.register(Follow)
