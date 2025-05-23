from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, Novel, Chapter,
    Category, CategoryNovel,
    UserNovel, Comment,ReadingProgress
)

# Custom admin cho CustomUser
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('sdt', 'is_admin')}),
    )
    list_display = ['username', 'email', 'sdt', 'is_admin', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'sdt']
    list_filter = ['is_admin', 'is_staff', 'is_superuser']
    ordering = ['username']

admin.site.register(CustomUser, CustomUserAdmin)

# Admin cho Novel
@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ['NovelId', 'Name', 'Author', 'ChapCount', 'ViewCount', 'TotalComments', 'State', 'dateUpdate']
    search_fields = ['Name', 'Author']
    list_filter = ['State']
    ordering = ['-dateUpdate']

# Admin cho Chapter
@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['ChapId', 'Name', 'Novel', 'Number', 'dateUpdate']
    search_fields = ['Name', 'Novel__Name']
    list_filter = ['Novel']
    ordering = ['Novel', 'Number']

# Admin cho Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['CategoryId', 'Name']
    search_fields = ['Name']
    ordering = ['CategoryId']

# Admin cho CategoryNovel
@admin.register(CategoryNovel)
class CategoryNovelAdmin(admin.ModelAdmin):
    list_display = ['CNId', 'Novel', 'Category']
    list_filter = ['Category']
    search_fields = ['Novel__Name', 'Category__Name']

# Admin cho UserNovel
@admin.register(UserNovel)
class UserNovelAdmin(admin.ModelAdmin):
    list_display = ['UNId', 'User', 'Novel']
    search_fields = ['User__username', 'Novel__Name']

# Admin cho Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['_id', 'User', 'Novel', 'CommentId', 'CreatedAt', 'parent_comment']
    search_fields = ['Content', 'User__username', 'Novel__Name']
    list_filter = ['CreatedAt']
    ordering = ['-CreatedAt']

@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'novel', 'current_chapter', 'updated_at')
    list_filter = ('novel', 'updated_at')