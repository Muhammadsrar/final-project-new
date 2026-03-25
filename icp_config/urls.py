# urls.py

from django.urls import path
from . import views  # Import your views from the current app

urlpatterns = [
    path('icp_config/', views.icp_config, name='icp_config'),
    path('icp_edit/<int:profile_id>/', views.icp_edit, name='icp_edit'),  # For editing existing profiles
    path('icp_config/<int:profile_id>/', views.icp_config, name='icp_config'),  # For editing existing profiles
    path('icp_delete/<int:profile_id>/', views.icp_delete, name='icp_delete'),  # For deleting profiles

    # path('icp_create/', views.icp_create, name='icp_create'),
    path('icp_list/', views.icp_list, name='icp_list'),  # new separate list view
]