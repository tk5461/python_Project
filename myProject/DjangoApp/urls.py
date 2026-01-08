from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name='home'),
    path("register/", views.register, name='register'),
    path("login/", views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('tasks/', views.all_task, name='tasks'),
    path('addTask/', views.add_task, name='addTask'),
    path('tasks/<int:task_id>/', views.edit_task, name='editTask'),
    path('tasks/<int:id>/edit', views.delete_task, name='delete_task'),
    path('update_task_status/<int:id>/', views.update_task_status, name='update_task_status'),
    path('update_task_executor/<int:id>/', views.update_task_executor, name='update_task_executor'),
    path('update_task/<int:id>/', views.update_task_executor, name='update_task_executor'),
    # path('filter_tasks_By_Status/', views.TaskFilterByStatus, name='filter_tasks_By_Status'),
    # path('filter_tasks_By_executor/', views.filter, name='filter_tasks_By_executor')
    path('filter/', views.filter, name='filter_tasks_By_Status')

]

