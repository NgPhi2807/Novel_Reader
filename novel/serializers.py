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
    categories = serializers.SerializerMethodField()  # Lấy danh sách category của Novel

    class Meta:
        model = Novel
        fields = [
            'NovelId', 'Name', 'ViewCount', 'Description', 'Author', 
            'State', 'ChapCount', 'ImgUrl', 'dateUpdate', 'TotalComments', 
            'latest_chapter', 'latest_update_display', 'categories'
        ]

    def get_latest_chapter(self, obj):
        """ Lấy chương mới nhất theo dateUpdate (nếu trùng thì lấy Number cao nhất) """
        latest_chapter = Chapter.objects.filter(Novel=obj).order_by('-dateUpdate', '-Number').first()
        return ChapterSerializer(latest_chapter).data if latest_chapter else None

    def get_categories(self, obj):
    
       category_ids = CategoryNovel.objects.filter(Novel=obj).values_list('Category_id', flat=True)  # Lấy danh sách ID thể loại
       categories = Category.objects.filter(CategoryId__in=category_ids)  # Chỉ lấy thể loại có ID khớp với Novel
       return CategorySerializer(categories, many=True).data
