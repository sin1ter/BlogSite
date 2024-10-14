from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Count, Q, Value, IntegerField
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.utils.decorators import method_decorator

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required

from accounts.models import MyUser
from .models import Blog, Tag, Comment, Reply, Like, FeatureRequest
from .forms import CreateBlog, CreateComment, ReplyComment

def is_admin(user):
    return user.is_authenticated and user.is_admin

class IndexView(ListView):
    model = Blog
    template_name = 'blogs/index.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q', '')
        selected_tag = self.request.GET.get('tag', '')
        user = self.request.user

        # Annotate with like counts
        blogs = Blog.objects.annotate(
            like_count=Count('likes'),
        ).order_by('-created_at')

        if user.is_authenticated:
            # Check if the blog is liked by the user
            blogs = blogs.annotate(
                is_liked=Count('likes', filter=Q(likes__user=user))
            )
        else:
            blogs = blogs.annotate(is_liked=Value(0, output_field=IntegerField()))

        if query:
            blogs = blogs.filter(title__icontains=query)

        if selected_tag:
            blogs = blogs.filter(tags__name=selected_tag)

        return blogs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()  
        return context
    
    def get_paginate_by(self, queryset):
        records_per_page = self.request.GET.get('records')
        if records_per_page:
            return int(records_per_page)
        return self.paginate_by

class FeatureBlogListView(ListView):
    model = Blog
    template_name = 'blogs/feature_blogs.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        queryset = Blog.objects.filter(featured=True).order_by('created_at')
        return queryset
    

class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/blog_detail.html'
    context_object_name = 'blog'

class BlogCreateView(LoginRequiredMixin, CreateView):
    model = Blog  
    form_class = CreateBlog  
    template_name = 'blogs/create_blog.html'  
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        blog = form.save(commit=False)
        blog.author = self.request.user
        blog.save()
        form.save_m2m()

        if form.cleaned_data.get('feature_request'):
            FeatureRequest.objects.create(
                blog=blog,
                user=self.request.user,
                requested_at=timezone.now(),
                status='pending',
            )
        return super().form_valid(form)


class OwnBlogView(LoginRequiredMixin, ListView):
    model = Blog
    template_name = 'blogs/my_blogs.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        queryset = Blog.objects.filter(author=self.request.user)
        return queryset
    

class BlogUpdateView(LoginRequiredMixin, UpdateView):
    model = Blog
    template_name = 'blogs/update_blog.html'
    fields = ['title', 'content', 'tags', 'images']
    success_url = reverse_lazy('own_blog')

@login_required
def BlogDeleteView(request, id):
    blog = get_object_or_404(Blog, id=id)
    if request.method == 'POST':
        blog.delete()
        return redirect(reverse('own_blog'))
    return redirect(reverse('own_blog'))

def like_blog(request, blog_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))
        
    blog = get_object_or_404(Blog, id=blog_id)
    user = request.user

    liked = Like.objects.filter(blog=blog, user=user).exists()

    if liked:
        Like.objects.filter(blog=blog, user=user).delete()
    else:
        Like.objects.create(blog=blog, user=user)


    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def CommentView(request, id):
    blog = get_object_or_404(Blog, id=id)
    form = CreateComment(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.blog = blog
        comment.user = request.user
        comment.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'blog': blog,
        'form': form,
        'comments': blog.comments.all(),
    }
    return render(request, 'blogs/blog_detail.html', context)

@login_required
def CommentDelete(request, id):
    comment = get_object_or_404(Comment, id=id)
    blog = comment.blog
    if comment.user == request.user or blog.author == request.user:
        if request.method == 'POST':
            comment.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def ReplyDelete(request, id):

    reply = get_object_or_404(Reply, id=id)
    comment = reply.comment
    blog = comment.blog

    if reply.user == request.user or blog.author == request.user:
        if request.method == 'POST':
            reply.delete()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def ReplyView(request, id):
    comment = get_object_or_404(Comment, id=id)
    form = ReplyComment(request.POST or None)
    if form.is_valid():
        reply = form.save(commit=False)
        reply.comment = comment
        reply.user = request.user
        reply.save()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    context = {
        'comment': comment,
        'form': form,
        'comments': comment.replies.all(),
    }
    return render(request, 'blogs/blog_detail.html', context)


# admin
@login_required
@user_passes_test(is_admin)
def dashboard(reqeust):
    blogs = Blog.objects.count()
    tags = Tag.objects.count()
    likes = Like.objects.count()
    users = MyUser.objects.count()
    featured = Blog.objects.filter(featured=True).count()
    featured_request = Blog.objects.filter(feature_request=True).count()
    pending_feature = FeatureRequest.objects.filter(status='pending').count()
    approved_feature = FeatureRequest.objects.filter(status='approved').count()
    reject_feature = FeatureRequest.objects.filter(status='rejected').count()
    context = {
        'blogs': blogs,
        'tags': tags,
        'likes': likes,
        'users': users,
        'featured': featured,
        'featured_request' : featured_request,
        'pending_feature' : pending_feature,
        'approved_feature' : approved_feature,
        'reject_feature' : reject_feature,
    }
    return render(reqeust, 'blogs/dashboard.html', context)

class TagListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Tag
    template_name = "blogs/tag_list.html"
    context_object_name = "tags"
    queryset = Tag.objects.annotate(blog_count=Count('blogs'))
    ordering = ['name']
    paginate_by = 10

    def get_queryset(self):
        return Tag.objects.all().annotate(blog_count=Count('blogs'))
    
    # Only allowing the admin to see the tags
    
    def test_func(self):
        return self.request.user.is_admin

    # if the user is not the admin redirect to the home page or login page
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()

class TagCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Tag
    fields = ['name']
    template_name = "blogs/add_tag.html"
    success_url = reverse_lazy('dashboard')

    # Only allowing the admin to create tag
    def test_func(self):
        return self.request.user.is_admin
    
    # if the user is not the admin redirect to the home page or login page
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()

class TagUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Tag
    fields = ['name']
    template_name = "blogs/update_tag.html"
    success_url = reverse_lazy('tag_list')
    
    # Only allowing the admin to update tag
    def test_func(self):
        return self.request.user.is_admin
    
    # if the user is not the admin redirect to the home page or login page
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()


@login_required
@user_passes_test(is_admin)
def activate_tag(request, id):
    tag = get_object_or_404(Tag, id=id)
    if tag.is_active == True:
        tag.is_active = False
    else:
        tag.is_active = True
    tag.save()

    return redirect('tag_list')

@login_required
@user_passes_test(is_admin)
def delete_tag(request, id):
    tag = get_object_or_404(Tag, id=id)
    tag.delete()
    return redirect('tag_list')


class FeatureRequestListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = FeatureRequest
    template_name = "blogs/feature_request.html"
    context_object_name = "feature_requests"
    ordering = ['-requested_at']   
    
    # Only allowing admin to view the list
    def test_func(self):
        return self.request.user.is_admin

    # if the user is not the admin redirect to the home page or login page    
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()


@login_required
@user_passes_test(is_admin)
def approve_feature_requests(request, id):
    feature_request = get_object_or_404(FeatureRequest, id=id)
    feature_request.approve(reviewer=request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
@login_required
@user_passes_test(is_admin)
def reject_feature_requests(request, id):
    feature_request = get_object_or_404(FeatureRequest, id=id)
    feature_request.reject(reviewer=request.user)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MyUser
    template_name = "blogs/user_list.html"
    context_object_name = "users"
    ordering = ['username']
    
    # Only allowing admin to view the list
    def test_func(self):
        return self.request.user.is_admin
    
    # if the user is not the admin redirect to the home page or login page
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()
    
class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MyUser
    template_name = "blogs/user_detail.html"
    context_object_name = "user"
    
    # Only allowing admin to view the user details
    def test_func(self):
        return self.request.user.is_admin
    
    # if the user is not the admin redirect to the home page or login page
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('home')
        else:
            return super().handle_no_permission()
    
@login_required
@user_passes_test(is_admin)
def UserDeleteView(request, pk):
    user = get_object_or_404(MyUser, pk=pk)
    user.delete()
    return redirect('users')

@login_required
@user_passes_test(is_admin)
def Report(request):
    blog_count = Blog.objects.all().count() 
    user = MyUser.objects.all().count()
    all_tag = Tag.objects.all().count()
    active_tag = Tag.objects.filter(is_active=True).count()
    most_written_blog = MyUser.objects.annotate(blog_count=Count('blog')).order_by('-blog_count').first()
    most_liked_blog = Blog.objects.annotate(like_count=Count('likes')).order_by('-like_count').first()

    context = {
        'blog_count' : blog_count,
        'user' : user, 
        'all_tag' : all_tag, 
        'active_tag' : active_tag,
        'most_written_blog' : most_written_blog,
        'most_written_blog_count' : most_written_blog.blog_count, 
        'most_liked_blog' : most_liked_blog
    }

    return render(request, 'blogs/report.html', context)

@login_required
# @user_passes_test(is_admin)
def Leaderboard(request):
    users = MyUser.objects.annotate(blog_count=Count('blog')).order_by('-blog_count')[:5]
    most_liked_blogs = Blog.objects.annotate(like_count=Count('likes')).order_by('-like_count')[:5]

    context = {
        'users': users,
        'most_liked_blogs' : most_liked_blogs

    }
    return render(request, 'blogs/leaderboard.html', context)