from django.urls import path
from . import views
from .views import get_chapter, update_chapter, list_chapter,delete_chapter


urlpatterns = [

    path("admin/", views.novel_list, name="novel_list"),  # Danh sách truyện
    path("create/", views.add_novel, name="novel_create"),  # Tạo truyện mới
    path(
        "edit/<int:novel_id>/", views.edit_novel, name="novel_edit"
    ),  
    # Chi tiết truyện
    path("<int:novel_id>/list_chapter/", views.list_chapter, name="list_chapter"),

 
    path("", views.user_home, name="user_home"),
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
]
