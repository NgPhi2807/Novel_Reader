from django.urls import path
from . import views_admin, views_user
from .views_admin import (
    get_chapter, update_chapter, list_chapter, delete_chapter,
    admin_dashboard, user_list,toggle_admin , delete_novel_and_related
)
from .views_user import (
    register_user, login_view, logout_view,
    password_reset_request, password_reset_verify, password_reset_confirm,
    search_novel, UserHomeView ,add_comment_reply
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version='v1',
        description="Description of the API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path('api/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-docs'),
    # 🌟 Trang chính
    path("", views_user.user_home, name="user_home"),
    path('api/user_home/', UserHomeView.as_view(), name='user_home_api'),


    # 🌟 Quản lý người dùng
    path('register/', register_user, name='register_user'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user_home/', views_user.user_home, name='user_home'),
    path('toggle-admin/<int:user_id>/', views_admin.toggle_admin, name='toggle_admin'),


    # 🔐 Quản lý mật khẩu
    path("password_reset/", password_reset_request, name="password_reset"),
    path("password_reset/verify/", password_reset_verify, name="password_reset_verify"),
    path('password_reset/confirm/', password_reset_confirm, name='password_reset_confirm'),

    # 📚 Quản lý truyện 
    path('admin/', views_admin.novel_list, name='novel_list'),
    path("create/", views_admin.add_novel, name="novel_create"),
    path("edit/<int:novel_id>/", views_admin.edit_novel, name="novel_edit"),

    # User view 
    path('all-novels/', views_user.all_novel, name='all_novel'),
    path('search/', views_user.search_novel, name='search_novel'),


    # 📊 Quản lý Admin Dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/userlist/', user_list, name='user_list'),
    path('admin/<int:user_id>/delete/', views_admin.delete_user, name='delete_user'),
    path('delete_novel/<int:novel_id>', views_admin.delete_novel_and_related, name='delete_novel'),

    # 📖 Chi tiết truyện
    path("detail/<int:novel_id>/", views_user.user_novel_detail, name="user_novel_detail"),
    path('comment/<int:CommnetId>/reply/', views_user.add_comment_reply, name='reply_comment'),

    
    # 📖 Quản lý chương truyện
    path("<int:novel_id>/list_chapter/", list_chapter, name="list_chapter"),
    path("<int:novel_id>/list_chapter/get_chapter/<int:chapter_id>/", get_chapter, name="get_chapter"),
    path("<int:novel_id>/list_chapter/update/<int:chap_id>/", update_chapter, name="update_chapter"),
    path("<int:novel_id>/add_chapter/add/", views_admin.add_chapter, name="add_chapter"),
    path('<int:novel_id>/list_chapter/delete/<int:chap_id>/', delete_chapter, name='delete_chapter'),

    # ⏭️ Điều hướng chương truyện
    path("detail/<int:novel_id>/<int:chapter_id>/", views_user.user_chapter_detail, name="user_chapter_detail"),
    path('next_chapter/<int:novel_id>/<int:chapter_id>/', views_user.get_next_chapter, name='get_next_chapter'),
    path('prev_chapter/<int:novel_id>/<int:chapter_id>/', views_user.get_prev_chapter, name='get_prev_chapter'),
]
