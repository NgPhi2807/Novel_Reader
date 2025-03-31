from django.urls import path
from . import views
from .views import get_chapter, update_chapter, list_chapter,delete_chapter,admin_dashboard,register_user,user_page,login_view,logout_view,password_reset_request,password_reset_verify,password_reset_confirm,user_list
from django.contrib.auth import views as auth_views



urlpatterns = [

    path('admin/', views.novel_list, name='novel_list'),  # Danh sách truyện
    path("create/", views.add_novel, name="novel_create"),  # Tạo truyện mới
    path(
        "edit/<int:novel_id>/", views.edit_novel, name="novel_edit"
    ),  

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/profile/', views.user_list, name='user_list'),
    path('register/', views.register_user, name='register_user'),
    path('user/', views.user_page, name='user_page'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('novel_list/', views.novel_list, name='novel_list'),  # Trang admin
    path('user_home/', views.user_home, name='user_home'),  # Trang người dùng

    path("password_reset/", views.password_reset_request, name="password_reset"),
    path("password_reset/verify/", views.password_reset_verify, name="password_reset_verify"),
    path('password_reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    
    # Chi tiết truyện
    path("<int:novel_id>/list_chapter/", views.list_chapter, name="list_chapter"),
    
    path("", views.user_home, name="user_home"),
    path('all-novels/', views.all_novel, name='all_novel'),  # Thêm đường dẫn này

    path("detail/<int:novel_id>/", views.user_novel_detail, name="user_novel_detail"),
    
    path("detail/<int:novel_id>/<int:chapter_id>", views.user_chapter_detail, name="user_chapter_detail"),
     path('next_chapter/<int:novel_id>/<int:chapter_id>/', views.get_next_chapter, name='get_next_chapter'),
    path('prev_chapter/<int:novel_id>/<int:chapter_id>/', views.get_prev_chapter, name='get_prev_chapter'),

    path(
        "<int:novel_id>/list_chapter/get_chapter/<int:chapter_id>/",
        views.get_chapter,
        name="get_chapter",
    ),
    path(
        "<int:novel_id>/list_chapter/update/<int:chap_id>/",
        views.update_chapter,
        name="update_chapter",
    ),
    path("<int:novel_id>/add_chapter/add/", views.add_chapter, name="add_chapter"),
    path('<int:novel_id>/list_chapter/delete/<int:chap_id>/', delete_chapter, name='delete_chapter'),  # URL mới
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    
]
