from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from django.db import IntegrityError

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
        try:
            search_query_int = int(search_query)
            novels_list = Novel.objects.filter(Name__icontains=search_query) | \
                          Novel.objects.filter(NovelId=search_query_int)
        except ValueError:
            novels_list = Novel.objects.filter(Name__icontains=search_query)
    else:
        novels_list = Novel.objects.all()

    novels_list = novels_list.order_by("NovelId")

    # Phân trang với 5 mục mỗi trang
    paginator = Paginator(novels_list, 5)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # Tính toán giới hạn cho phân trang từ 1 đến 10, 11 đến 20, v.v.
    start_page = (page_obj.number // 10) * 10 + 1  # Trang bắt đầu của nhóm
    end_page = start_page + 9  # Trang kết thúc của nhóm
    if end_page > paginator.num_pages:
        end_page = paginator.num_pages

    # Cập nhật page_obj để chỉ hiển thị nhóm trang từ start_page đến end_page
    page_range = range(start_page, end_page + 1)

    return render(request, "novel/Admin/novel_list.html", {
        "page_obj": page_obj,
        "search_query": search_query,
        "page_range": page_range,
    })



@admin_required
def edit_novel(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)
    categories = Category.objects.all()  # Lấy tất cả các thể loại
    selected_categories = CategoryNovel.objects.filter(Novel=novel).values_list(
        "Category_id", flat=True
    )

    if request.method == "POST":
        # Cập nhật các trường của truyện
        novel.Name = request.POST.get("name")
        novel.Author = request.POST.get("author")
        novel.Description = request.POST.get("description")
        img = request.FILES.get("img")
        if img:
            novel.ImgUrl = img

        novel.save()

        # Lấy danh sách ID thể loại từ request (ví dụ: "1,2")
        category_ids_str = request.POST.get("categories", "")
        selected_category_ids = category_ids_str.split(",") if category_ids_str else []

        # Xóa các liên kết thể loại cũ
        CategoryNovel.objects.filter(Novel=novel).delete()

        # Lấy CNId lớn nhất hiện tại và cộng thêm 1
        last_cn_id = CategoryNovel.objects.order_by("-CNId").first()
        next_cn_id = last_cn_id.CNId + 1 if last_cn_id else 1

        # Thêm các liên kết thể loại mới với CNId tự tăng
        for category_id in selected_category_ids:
            if category_id:  # Kiểm tra ID không trống
                try:
                    category = Category.objects.get(pk=category_id)
                    # Tạo liên kết với CNId tự tăng
                    CategoryNovel.objects.create(
                        CNId=next_cn_id,  # Gán CNId tự tăng
                        Novel=novel,
                        Category=category
                    )
                    next_cn_id += 1  # Tăng CNId cho lần kế tiếp
                except (Category.DoesNotExist, ValueError):
                    # Bỏ qua các ID thể loại không hợp lệ hoặc không tồn tại
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
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()
        author = request.POST.get("author", "").strip()
        state = request.POST.get("state", "").strip()
        img = request.FILES.get("img")
        category_ids = request.POST.get("categories", "")

        if not name or not description or not author or not state:
            return HttpResponse("Vui lòng điền đầy đủ thông tin.")

        # Lấy NovelId lớn nhất hiện tại
        last_novel = Novel.objects.order_by("-NovelId").first()
        next_novel_id = last_novel.NovelId + 1 if last_novel else 1

        # Tạo tiểu thuyết mới với NovelId tự tăng
        novel = Novel(
            NovelId=next_novel_id,  # Gán NovelId tự động tăng
            Name=name,
            Description=description,
            Author=author,
            State=state,
            ChapCount=0,
        )

        if img:
            novel.ImgUrl = img

        try:
            novel.save() 
        except IntegrityError:
            return HttpResponse("Lỗi: Không thể lưu tiểu thuyết, vui lòng thử lại.")
        
        if not hasattr(novel, 'NovelId'):
            return HttpResponse("Lỗi: Không thể gán NovelId cho tiểu thuyết.")

        novel_id = novel.NovelId  

        # Xử lý thể loại
        if not category_ids:
            return HttpResponse("Vui lòng chọn ít nhất một thể loại.")

        category_ids = [int(cat_id) for cat_id in category_ids.split(",") if cat_id.isdigit()]
        
        # Kiểm tra nếu không có thể loại hợp lệ
        if not category_ids:
            return HttpResponse("Không có thể loại hợp lệ được chọn.")

        # Lấy CNId lớn nhất hiện tại
        last_cn_id = CategoryNovel.objects.order_by("-CNId").first()
        next_cn_id = last_cn_id.CNId + 1 if last_cn_id else 1

        # Tạo mối quan hệ CategoryNovel
        for category_id in category_ids:
            category = Category.objects.filter(pk=category_id).first()
            if category:
                CategoryNovel.objects.create(CNId=next_cn_id, Novel_id=novel_id, Category=category)
                next_cn_id += 1

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
def delete_novel_and_related(request, novel_id):
    # Lấy cuốn tiểu thuyết theo ID
    novel = get_object_or_404(Novel, NovelId=novel_id)

    # Tiến hành xóa cuốn tiểu thuyết và các đối tượng liên quan (Chapters, Comments, etc.)
    # Xóa các chapter liên quan
    novel.chapter_set.all().delete()
    # Xóa các bình luận liên quan
    novel.comment_set.all().delete()
    # Sau đó xóa cuốn tiểu thuyết
    novel.delete()

    # Redirect đến trang danh sách tiểu thuyết hoặc trang quản lý
    return redirect('novel_list')
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

@admin_required
def toggle_admin(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if not user.is_superuser:  # Không cho phép thay đổi quyền của Superuser
        user.is_admin = not user.is_admin  # Đảo trạng thái Admin
        user.save()
    return redirect('user_list')


