import os
from django.conf import settings

from django.db import models
from django.utils import timezone

from accounts.models import MyUser


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    

class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    images = models.ImageField(null=True, blank=True, upload_to='blog_images/')
    author = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)
    feature_request = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', related_name='blogs')
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        if self.images:
            image_path = os.path.join(settings.MEDIA_ROOT, self.images.path)
            if os.path.exists(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)

class FeatureRequest(models.Model):
    blog = models.ForeignKey(Blog, related_name='feature_requests', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')

    def approve(self, reviewer):
        self.status = 'approved'
        self.reviewed_at = timezone.now()
        self.blog.featured = True
        self.blog.save()
        self.save()

    def reject(self, reviewer):
        self.status = 'rejected'
        self.reviewed_at = timezone.now()
        self.blog.featured = False
        self.blog.save()
        self.save()

    def __str__(self):
        return f'Feature Request by {self.user.username} for {self.blog.title}'
    
    def __str__(self):
        return f'Feature Request by {self.user.username} on {self.blog.title}'

class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.blog.title}'

class Reply(models.Model):
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=254)
    parent_reply = models.ForeignKey('self', null=True, blank=True, related_name='sub_replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Reply by {self.user.username} on {self.comment.blog.title}'

class Like(models.Model):
    blog = models.ForeignKey(Blog, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Like by {self.user.username} on {self.blog.title}'

class BlogView(models.Model):
    blog = models.ForeignKey(Blog, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'View by {self.user.username} on {self.blog.title}'
