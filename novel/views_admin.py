from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from .models import Novel, Category, CategoryNovel, Chapter, CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_admin:
            return render(request, "novel/404.html")  
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
@csrf_exempt
def update_chapter(request, novel_id, chap_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            chapter = Chapter.objects.get(ChapId=chap_id, Novel_id=novel_id)

            chapter.Name = data.get("name", chapter.Name)
            chapter.Content = data.get("content", chapter.Content)
            chapter.save()

            return JsonResponse({"status": "success"})
        except Chapter.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Không tìm thấy chương!"}, status=404
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Dữ liệu không hợp lệ!"}, status=400
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Chỉ hỗ trợ POST!"}, status=405)

@admin_required
@require_POST
def add_chapter(request, novel_id):
    try:
        data = json.loads(request.body)
        name = data.get('name')
        number = data.get('number')
        content = data.get('content')

        if not all([name, number, content]):
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin bắt buộc'}, status=400)

        novel = get_object_or_404(Novel, NovelId=novel_id)
        if Chapter.objects.filter(Novel=novel, Number=number).exists():
            return JsonResponse({'status': 'error', 'message': 'Số chương đã tồn tại'}, status=400)

        # Tạo chương mới
        chapter = Chapter.objects.create(
            Novel=novel,
            Name=name,
            Number=number,
            Content=content
        )

        # Cập nhật ChapCount cho novel
        novel.ChapCount = Chapter.objects.filter(Novel=novel).count()
        novel.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Thêm chương thành công',
            'chapter_id': chapter.ChapId
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@admin_required
@require_POST
def delete_chapter(request, novel_id, chap_id):
    try:
        # Lấy chapter dựa trên chap_id và novel_id
        chapter = get_object_or_404(Chapter, ChapId=chap_id, Novel__NovelId=novel_id)
        chapter.delete()  # Xóa chapter khỏi database

        return JsonResponse({"status": "success", "message": "Xóa chương thành công"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

@admin_required
def novel_list(request):
    search_query = request.GET.get('search', '').strip()
    
    # Lọc dữ liệu theo từ khóa tìm kiếm
    if search_query:
        novels_list = Novel.objects.filter(Name__icontains=search_query) | \
                      Novel.objects.filter(NovelId__icontains=search_query)
    else:
        novels_list = Novel.objects.all()

    # Sắp xếp theo NovelId giảm dần
    novels_list = novels_list.order_by("-NovelId")

    # Phân trang
    paginator = Paginator(novels_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "novel/Admin/novel_list.html", {"page_obj": page_obj, "search_query": search_query})

@admin_required
def edit_novel(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)
    categories = Category.objects.all()  # Fetch all categories
    selected_categories = CategoryNovel.objects.filter(Novel=novel).values_list(
        "Category_id", flat=True
    )

    if request.method == "POST":
        # Update novel fields
        novel.Name = request.POST.get("name")
        novel.Author = request.POST.get("author")
        novel.Description = request.POST.get("description")
        img = request.FILES.get("img")
        if img:
            novel.ImgUrl = img

        novel.save()

        # Get the comma-separated category IDs and split them
        category_ids_str = request.POST.get("categories", "")  # e.g., "1,2"
        selected_category_ids = category_ids_str.split(",") if category_ids_str else []

        # Remove existing category associations
        CategoryNovel.objects.filter(Novel=novel).delete()

        # Add new category associations
        for category_id in selected_category_ids:
            if category_id:  # Ensure the ID is not empty
                try:
                    category = Category.objects.get(pk=category_id)
                    CategoryNovel.objects.create(Novel=novel, Category=category)
                except (Category.DoesNotExist, ValueError):
                    # Skip invalid or non-existent category IDs
                    continue

        return redirect("novel_list")

    return render(
        request,
        "novel/Admin/novel_edit.html",
        {
            "novel": novel,
            "categories": categories,
            "selected_categories": selected_categories,
        },
    )

@admin_required
def add_novel(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        author = request.POST.get("author")
        state = request.POST.get("state")
        chap_count = 0

        img = request.FILES.get("img")
        category_ids = request.POST.get("categories", "")

        # Chuyển chuỗi thành danh sách số nguyên
        category_ids = category_ids.split(",")
        category_ids = [int(cat_id) for cat_id in category_ids if cat_id.isdigit()]

        # Tạo NovelId mới (bạn có thể thay thế bằng logic tạo id phù hợp)
        novel_id = Novel.objects.count() + 1  # Sử dụng một phương pháp thích hợp để tạo id duy nhất.

        novel = Novel(
            NovelId=novel_id,
            Name=name,
            Description=description,
            Author=author,
            State=state,
            ChapCount=int(chap_count) if chap_count else 0,
        )

        if img:
            novel.ImgUrl = img
        try:
            novel.save()
        except IntegrityError:
            return HttpResponse("NovelId already exists, please try again.")

        # Liên kết thể loại
        for category_id in category_ids:
            category = Category.objects.get(pk=category_id)
            CategoryNovel.objects.create(Novel=novel, Category=category)

        return redirect("novel_list")

    categories = Category.objects.all()
    return render(request, "novel/Admin/novel_create.html", {"categories": categories})

@admin_required
def list_chapter(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)
    chapters = Chapter.objects.filter(Novel=novel).order_by("Number")
    if request.method == "POST":
        name = request.POST.get("name")
        number = request.POST.get("number")
        content = request.POST.get("content")

        if name and number and content:  # Kiểm tra dữ liệu hợp lệ
            Chapter.objects.create(
                Novel=novel, Name=name, Number=number, Content=content
            )
            return redirect("novel_list")

    return render(
        request, "novel/Admin/chapter_add.html", {"novel": novel, "chapters": chapters}
    )

@admin_required
def get_chapter(request, novel_id, chapter_id):
    chapter = get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id)
    return JsonResponse({"name": chapter.Name, "content": chapter.Content})

@admin_required    
def user_list(request):
    search_query = request.GET.get('search', '').strip()
    
    if search_query:
        users = User.objects.filter(username__icontains=search_query) | \
                User.objects.filter(email__icontains=search_query)
    else:
        users = User.objects.all()
    
    return render(request, "novel/Admin/user_list.html", {
        "users": users,
        "search_query": search_query
    })

@admin_required
def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)

        if user.is_superuser:  
            return JsonResponse({"error": "Không thể xóa admin"}, status=403)

        user.delete()
        messages.success(request, "Xóa người dùng thành công!")  # Sử dụng messages
        return redirect("user_list")  

    return JsonResponse({"error": "Yêu cầu không hợp lệ"}, status=400)

@admin_required
def admin_dashboard(request):
    users_count = CustomUser.objects.count()
    novels_count = Novel.objects.count()
    chapters_count = Chapter.objects.count()

    context = {
        "users_count": users_count,
        "novels_count": novels_count,
        "chapters_count": chapters_count,
    }

    return render(request, "novel/Admin/dashboard.html", context)