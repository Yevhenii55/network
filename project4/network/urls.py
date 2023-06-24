
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_post/', views.create_post_view, name='create_post'),
    path('all_posts/', views.all_posts_view, name='all_posts'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow_user'),
    path('following/', views.subscriptions_view, name='following'),    
    path('update_post/', views.update_post, name='update_post'),
    path('posts/', views.posts, name='posts'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),

]    
                              