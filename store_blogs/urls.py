from django.urls import path

from .views import (IndexView, BlogCreateView, BlogDetailView, 
                    CommentView,CommentDelete, ReplyView, ReplyDelete, like_blog,
                    OwnBlogView, BlogUpdateView, BlogDeleteView, dashboard, TagListView, TagCreateView, TagUpdateView, 
                    activate_tag, delete_tag, 
                    FeatureBlogListView, FeatureRequestListView, approve_feature_requests, reject_feature_requests,
                    UserListView, UserDetailView, UserDeleteView, 
                    Report, Leaderboard)

urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    path('detail/<int:pk>/', BlogDetailView.as_view(), name='detail_blog'),
    path('comment/<int:id>/', CommentView, name='add_comment'),
    path('delete-comment/<int:id>/', CommentDelete, name='delete_comment'),
    path('reply/<int:id>/', ReplyView, name='add_reply'),
    path('delete-reply/<int:id>/', ReplyDelete, name='delete_reply'),
    path('blog/<int:blog_id>/like/', like_blog, name='like_blog'),
    path('create-blog/', BlogCreateView.as_view(), name='create_blog'),
    path('own-blog/', OwnBlogView.as_view(), name='own_blog'),
    path('edit-blog/<int:pk>/', BlogUpdateView.as_view(), name='edit_blog'),
    path('delete-blog/<int:id>/', BlogDeleteView, name='delete_blog'),

    path('dashboard/', dashboard, name='dashboard'),
    path('tag-list', TagListView.as_view(), name='tag_list'),
    path('add-tag/', TagCreateView.as_view(), name='add_tag'),
    path('update-tag/<int:pk>/', TagUpdateView.as_view(), name='update_tag'),
    path('tags/toggle/<int:id>/', activate_tag, name='toggle_tag'),
    path('tags/delete/<int:id>/',delete_tag, name='delete_tag'),

    path('featured/', FeatureBlogListView.as_view(), name='featured'),

    path('feature-request-list/', FeatureRequestListView.as_view(), name='feature_list'),
    path('approve-request/approve/<int:id>/', approve_feature_requests, name='approve_request'),
    path('reject-request/reject/<int:id>/', reject_feature_requests, name='reject_request'),

    path('user/', UserListView.as_view(), name='users'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user_details'),
    path('user-delete/<int:pk>/', UserDeleteView, name='delete_user'),

    path('report/', Report, name='reports'),
    path('leaderboard/', Leaderboard, name='leaderboard'),
]
