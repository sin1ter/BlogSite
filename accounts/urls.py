from django.urls import path
from .views import SignupView, ProfileUpdateView, home, profile, profile_view


urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('', home, name='account'),
    path('profile/', profile, name='profile'),
    path('update_profile/', ProfileUpdateView.as_view(), name='update_profile'),
    path('profile_view/<int:id>/', profile_view, name='profile_view')
]