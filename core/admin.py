from django.contrib import admin
from .models import Profile, Post, LikePost, FollowersCount, Message

class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'caption', 'is_spam', 'created_at')  # ← Customize this as per your fields
    list_filter = ('is_spam',)  # Optional: adds filter sidebar

admin.site.register(Profile)
admin.site.register(Post, PostAdmin)  # ← Use custom admin class here
admin.site.register(LikePost)
admin.site.register(FollowersCount)
admin.site.register(Message)
