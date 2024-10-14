from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UserCreationForm, UserChangeForm
from .models import MyUser
from store_blogs.models import Blog

class SignupView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = 'registration/signup.html'

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = MyUser
    form_class = UserChangeForm
    success_url = reverse_lazy("profile")
    template_name = "registration/update_profile.html"

    login_url = 'login'    

    def get_object(self, queryset=None):
        return self.request.user

def profile_view(request, id):
    profile_user = get_object_or_404(MyUser, id=id)
    blogs = Blog.objects.filter(author=profile_user)
    context = {
        'profile_user': profile_user,
        'blogs':blogs,
    }
    return render(request,'blogs/profile_view.html', context)


@login_required
def home(request):
    if request.user.is_authenticated:
        user = MyUser.objects.get(email=request.user.email)  
        context = {
            'user': user,
        }
    else:
        context = {
            'user': None,
        }

    return render(request, 'home.html', context)

def profile(request):
    if request.user.is_authenticated:
        user = MyUser.objects.get(email=request.user.email)
        context = {
            'user':user,
        }
    else:
        context = {
            'user': None,
        }

    return render(request, 'registration/profile.html', context)

