from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('staff-register/', views.staff_register, name='staff_register'),

    path('login/', views.user_login, name='login'),

    path('user-home/', views.user_home, name='user_home'),
    path('staff-home/', views.staff_home, name='staff_home'),
    path('admin-home/', views.admin_home, name='admin_home'),

    path('logout/', views.user_logout, name='user_logout'),
    path('staff-logout/', views.staff_logout, name='staff_logout'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    # User Management
path('manage-users/', views.manage_users, name='manage_users'),
path('view-user/<int:id>/', views.view_user, name='view_user'),
path('edit-user/<int:id>/', views.edit_user, name='edit_user'),
path('delete-user/<int:id>/', views.delete_user, name='delete_user'),
# Staff Management
path('manage-staff/', views.manage_staff, name='manage_staff'),
path('add-staff/', views.add_staff, name='add_staff'),
path('view-staff/<int:id>/', views.view_staff, name='view_staff'),
path('edit-staff/<int:id>/', views.edit_staff, name='edit_staff'),
path('delete-staff/<int:id>/', views.delete_staff, name='delete_staff'),
# Collection Centre Management
path('manage-centres/', views.manage_centres, name='manage_centres'),
path('add-centre/', views.add_centre, name='add_centre'),
path('view-centre/<int:id>/', views.view_centre, name='view_centre'),
path('edit-centre/<int:id>/', views.edit_centre, name='edit_centre'),
path('delete-centre/<int:id>/', views.delete_centre, name='delete_centre'),
# Category Management
path('manage-categories/', views.manage_categories, name='manage_categories'),
path('add-category/', views.add_category, name='add_category'),
path('view-category/<int:id>/', views.view_category, name='view_category'),
path('edit-category/<int:id>/', views.edit_category, name='edit_category'),
path('delete-category/<int:id>/', views.delete_category, name='delete_category'),
path('manage-requests/', views.manage_requests, name='manage_requests'),
path('view-request/<int:id>/', views.view_request, name='view_request'),
path('edit-request/<int:id>/', views.edit_request, name='edit_request'),
path('delete-request/<int:id>/', views.delete_request, name='delete_request'),
path('manage-assignments/', views.manage_assignments, name='manage_assignments'),
path('add-assignment/', views.add_assignment, name='add_assignment'),
path('view-assignment/<int:id>/', views.view_assignment, name='view_assignment'),
path('edit-assignment/<int:id>/', views.edit_assignment, name='edit_assignment'),
path('delete-assignment/<int:id>/', views.delete_assignment, name='delete_assignment'),
path('manage-collections/', views.manage_collections, name='manage_collections'),
path('add-collection/', views.add_collection, name='add_collection'),
path('view-collection/<int:id>/', views.view_collection, name='view_collection'),
path('edit-collection/<int:id>/', views.edit_collection, name='edit_collection'),
path('delete-collection/<int:id>/', views.delete_collection, name='delete_collection'),
path('manage-recycling/', views.manage_recycling, name='manage_recycling'),
path('add-recycling/', views.add_recycling, name='add_recycling'),
path('view-recycling/<int:id>/', views.view_recycling, name='view_recycling'),
path('edit-recycling/<int:id>/', views.edit_recycling, name='edit_recycling'),
path('delete-recycling/<int:id>/', views.delete_recycling, name='delete_recycling'),
path('manage-feedback/', views.manage_feedback, name='manage_feedback'),
path('view-feedback/<int:id>/', views.view_feedback, name='view_feedback'),
path('edit-feedback/<int:id>/', views.edit_feedback, name='edit_feedback'),
path('delete-feedback/<int:id>/', views.delete_feedback, name='delete_feedback'),
path('user-home/', views.user_home, name='user_home'),

path('create-request/', views.create_collection_request, name='create_collection_request'),
path('my-requests/', views.my_requests, name='my_requests'),
path('track-request/<int:id>/', views.track_request, name='track_request'),

path('submit-feedback/<int:id>/', views.submit_feedback, name='submit_feedback'),

path('user-profile/', views.user_profile, name='user_profile'),
path('staff-home/', views.staff_home, name='staff_home'),

path('my-assignments/', views.my_assignments, name='my_assignments'),

path('staff-view-assignment/<int:id>/',
     views.staff_view_assignment,
     name='staff_view_assignment'),

path('update-assignment-status/<int:id>/',
     views.update_assignment_status,
     name='update_assignment_status'),

path('staff-profile/', views.staff_profile, name='staff_profile'),


]