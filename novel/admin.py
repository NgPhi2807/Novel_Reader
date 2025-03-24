from django.contrib import admin
from .models import Novel, Chapter, Category, CategoryNovel, User, UserNovel, Comment

admin.site.register(Novel)
admin.site.register(Chapter)
admin.site.register(Category)
admin.site.register(CategoryNovel)
admin.site.register(User)
admin.site.register(UserNovel)
admin.site.register(Comment)
