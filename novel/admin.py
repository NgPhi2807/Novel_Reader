from django.contrib import admin
from .models import Novel, Chapter

# Tạo lớp quản lý admin cho model Novel
class NovelAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Author', 'State', 'ChapCount', 'ViewCount', 'dateUpdate')
    search_fields = ('Name', 'Author')
    list_filter = ('State',)

    # Cấu hình phân quyền: chỉ admin mới có thể chỉnh sửa các đối tượng này
    def has_add_permission(self, request):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff thêm

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff thay đổi

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff xóa

# Đăng ký model Novel với cấu hình admin
admin.site.register(Novel, NovelAdmin)

# Tạo lớp quản lý admin cho model Chapter
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('Name', 'Number', 'Novel', 'dateUpdate')
    search_fields = ('Name', 'Novel__Name')  # Tìm kiếm theo tên chương và tên tiểu thuyết
    list_filter = ('Novel',)

    # Cấu hình phân quyền cho Chapter
    def has_add_permission(self, request):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff thêm chương mới

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff thay đổi chương

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff  # Chỉ cho phép người dùng có quyền staff xóa chương

# Đăng ký model Chapter với cấu hình admin
admin.site.register(Chapter, ChapterAdmin)
