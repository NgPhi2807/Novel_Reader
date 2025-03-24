from .models import Category
def base_data(request):
    categories = Category.objects.all()  
    return {'novels_base': categories}  