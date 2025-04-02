from rest_framework import serializers
from .models import Novel, Category, Chapter, CategoryNovel

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = ['ChapId', 'Name', 'Number', 'Content', 'dateUpdate']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['CategoryId', 'Name']

class NovelSerializer(serializers.ModelSerializer):
    latest_chapter = serializers.SerializerMethodField()  # Lấy chương mới nhất
    latest_update_display = serializers.CharField(source='dateUpdate', read_only=True)  # Hiển thị thời gian cập nhật
    categories = serializers.SerializerMethodField()  # Lấy danh sách category

    class Meta:
        model = Novel
        fields = [
            'NovelId', 'Name', 'ViewCount', 'Description', 'Author', 
            'State', 'ChapCount', 'ImgUrl', 'dateUpdate', 'TotalComments', 
            'latest_chapter', 'latest_update_display', 'categories'
        ]

    def get_latest_chapter(self, obj):
        # Lấy chương mới nhất dựa trên dateUpdate hoặc Number
        latest_chapter = Chapter.objects.filter(Novel=obj).order_by('-dateUpdate').first()
        if latest_chapter:
            return ChapterSerializer(latest_chapter).data
        return None

    def get_categories(self, obj):
        # Lấy tất cả category liên quan đến novel qua bảng CategoryNovel
        category_novels = CategoryNovel.objects.filter(Novel=obj)
        categories = [cn.Category for cn in category_novels]
        return CategorySerializer(categories, many=True).data