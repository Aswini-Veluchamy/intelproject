from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name="logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('home/', views.home, name='home'),
]