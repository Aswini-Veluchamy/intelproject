from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name="logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('home/', views.home, name='home'),
    path('key_message/', views.key_message, name='key_message'),
    path('risk/', views.risks, name='risk'),
    path('risk_edit_table/<str:pk>', views.risk_edit_table, name='risk_edit_table'),
    path('key_program/', views.key_program, name='key_program'),
    path('key_program_edit/<str:pk>', views.key_program_edit, name='key_program_edit'),
    path('key_program_delete/<str:pk>', views.key_program_delete, name='key_program_delete'),
    path('details/', views.details, name='details'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule_edit_table/<str:pk>', views.schedule_edit_table, name='schedule_edit_table'),
    path('links/', views.links, name='links'),
    path('links_edit_table/<str:pk>', views.links_edit_table, name='links_edit_table'),
    path('bbox/', views.bbox, name='bbox'),
    path('bbox_edit/<str:pk>', views.bbox_edit, name='bbox_edit'),
    path('issues/', views.issues, name='issues'),
    path('issues_edit_table/<str:pk>', views.issues_edit_table, name='issues_edit_table'),
    path('user_create/', views.user_create, name='user_create'),
    path('project/', views.project, name='project'),
    path('project_change/<str:func_name>', views.project_change, name='project_change'),
    path('delete_schedule_data/<str:pk>', views.delete_schedule_data, name='delete_schedule_data'),
    path('delete_issues_data/<str:pk>', views.delete_issues_data, name='delete_issues_data'),
    path('delete_links_data/<str:pk>', views.delete_links_data, name='delete_links_data')
]