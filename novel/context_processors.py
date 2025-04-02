from .models import Category

def base_data(request):
    """Trả về danh sách thể loại để dùng trong template"""
    return {"all_categories": Category.objects.all()}
