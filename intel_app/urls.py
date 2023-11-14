from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name="logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('home/', views.home, name='home'),
    path('key_message/', views.key_message, name='key_message'),
    path('key_edit_message/<str:pk>', views.key_edit_message, name='key_edit_message'),
    path('risk/', views.risks, name='risk'),
    path('risk_edit_table/<str:pk>', views.risk_edit_table, name='risk_edit_table'),
    path('key_program/', views.key_program, name='key_program'),
    path('key_program_edit/<str:pk>', views.key_program_edit, name='key_program_edit'),
    path('key_program_delete/<str:pk>', views.key_program_delete, name='key_program_delete'),
    path('details/', views.details, name='details'),
    path('details_edit_message/<str:pk>', views.details_edit_message, name='details_edit_message'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule_edit_table/<str:pk>', views.schedule_edit_table, name='schedule_edit_table'),
]