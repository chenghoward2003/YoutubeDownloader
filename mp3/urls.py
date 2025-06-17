from django.contrib import admin
from django.urls import include, path
from . import views, auth_views

urlpatterns = [
    path('mp3/', views.download_mp3, name='mp3'),
    path('mp4/', views.download_mp4, name='mp4'),
    path('delete/<int:content_id>/', views.delete_content, name='delete_content'),
    path('', views.index, name='home'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register')
]