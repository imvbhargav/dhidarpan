import uuid
from distutils.command.upload import upload
from email.policy import default
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


STATUS = (
    (0,"Draft"),
    (1,"Publish")
)

class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails', default='NULL.png')
    updated_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices = STATUS, default=0)
    likes = models.ManyToManyField(User, related_name='category_likes')

    class Meta:
        ordering = ['-created_on']

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("category_detail", kwargs={"slug": str(self.slug)})

class Post(models.Model):
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    thumbnail = models.ImageField(upload_to='thumbnails', default='NULL.png')
    author = models.ForeignKey(User, on_delete = models.CASCADE, related_name='blog_posts')
    categories = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category', default=0)
    updated_on = models.DateTimeField(auto_now=True)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices = STATUS, default=0)
    likes = models.ManyToManyField(User, related_name='blog_likes')
    class Meta:
        ordering = ['-created_on']

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("post_detail", kwargs={"slug": str(self.slug)})

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    commented_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['commented_on']
    
    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.commented_on)

class ProfileInfo(models.Model):
    user = models.OneToOneField(User, null=True, on_delete = models.CASCADE)
    bio = models.TextField()
    display_picture = models.ImageField(upload_to='profiles', default='profiles/NULL.png')
    website_url = models.CharField(max_length=200, null=True)
    facebook_url = models.CharField(max_length=200, null=True)
    twitter_url = models.CharField(max_length=200, null=True)
    youtube_url = models.CharField(max_length=200, null=True)
    linkedin_url = models.CharField(max_length=200, null=True)
    follows = models.ManyToManyField(User, related_name='follows')
    isGoogleUser = models.BooleanField(default=False)
    isSubscriber = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)
    
    def save_with_dp(self, *args, **kwargs):
        if self.pk:
            old_instance = ProfileInfo.objects.get(pk=self.pk)
            if self.display_picture != old_instance.display_picture:
                old_instance.display_picture.delete(save=False)

        if not self.display_picture:
            self.display_picture.name = "profiles/NULL.png"
        else:
            unique_filename = f"{self.user.id}_{self.user.username}_{uuid.uuid4().hex}.jpg"
            self.display_picture.name = unique_filename
        super(ProfileInfo, self).save(*args, **kwargs)

# Create your models here.
class Subscribers(models.Model):
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.email