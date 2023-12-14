from django.contrib import admin
from .models import Post, Comment, ProfileInfo, Category, Subscribers
from django_summernote.admin import SummernoteModelAdmin

class PostAdmin(SummernoteModelAdmin):
    list_display = ('title','slug','status','created_on')
    list_filter = ("status",)
    search_fields = ['title','content']
    prepopulated_fields = {'slug':('title',)}
    summernote_fields = ('content')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name','post','commented_on','active')
    list_filter = ('active', 'commented_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

class SubscribedUsersAdmin(admin.ModelAdmin):
    list_display = ('email',)

admin.site.register(Subscribers, SubscribedUsersAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(ProfileInfo)
admin.site.register(Category)
# Register your models here.
