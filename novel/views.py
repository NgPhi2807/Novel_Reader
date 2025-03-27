# Django core imports
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import localtime, now
from datetime import timedelta

# Import models from current app
from .models import Novel, Category, CategoryNovel, Chapter, CustomUser 

# Import forms from current app
from .forms import UserRegistrationForm
import json
import uuid


from django.http import HttpResponseForbidden

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Kiểm tra nếu người dùng không phải admin
        if not request.user.is_admin:
            return render(request, "novel/404.html")  # Trả về trang 404.html thay vì lỗi 403
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@admin_required
def admin_dashboard(request):
    users_count = CustomUser.objects.count()
    novels_count = Novel.objects.count()
    chapters_count = Chapter.objects.count()
    visits_count = VisitLog.objects.count()  # Đếm số lượt truy cập

    context = {
        "users_count": users_count,
        "novels_count": novels_count,
        "chapters_count": chapters_count,
        "visits_count": visits_count,
    }

    return render(request, "novel/dashboard.html", context)


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
@csrf_exempt
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
@csrf_exempt
@require_POST
def delete_chapter(request, novel_id, chap_id):
    try:
        # Lấy chapter dựa trên chap_id và novel_id
        chapter = get_object_or_404(Chapter, ChapId=chap_id, Novel__NovelId=novel_id)
        chapter.delete()  # Xóa chapter khỏi database

        return JsonResponse({"status": "success", "message": "Xóa chương thành công"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
def user_page(request):
    if request.user.is_admin:
        return redirect("login")  
    return render(request, "novel/User/user_novel_home.html")


@admin_required
def novel_list(request):
    novels_list = Novel.objects.all().order_by("-NovelId")
    paginator = Paginator(novels_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "novel/novel_list.html", {"page_obj": page_obj})


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
        "novel/novel_edit.html",
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

        novel = Novel(
            Name=name,
            Description=description,
            Author=author,
            State=state,
            ChapCount=int(chap_count) if chap_count else 0,
        )

        if img:
            novel.ImgUrl = img
        novel.save()

        # Liên kết thể loại
        for category_id in category_ids:
            category = Category.objects.get(pk=category_id)
            CategoryNovel.objects.create(Novel=novel, Category=category)

        return redirect("novel_list")

    categories = Category.objects.all()
    return render(request, "novel/novel_create.html", {"categories": categories})

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
        request, "novel/chapter_add.html", {"novel": novel, "chapters": chapters}
    )
@admin_required
def get_chapter(request, novel_id, chapter_id):
    chapter = (get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id),)
    return JsonResponse({"name": chapter.Name, "content": chapter.Content})

####   USER
def viet_timesince(time):
    if not time:
        return "Không có dữ liệu"

    delta = now() - time

    if delta < timedelta(minutes=1):
        return "Vừa xong"
    elif delta < timedelta(hours=1):
        return f"{int(delta.total_seconds() // 60)} phút trước"
    elif delta < timedelta(days=1):
        return f"{int(delta.total_seconds() // 3600)} giờ trước"
    elif delta < timedelta(days=30):
        return f"{delta.days} ngày trước"
    elif delta < timedelta(days=365):
        return f"{delta.days // 30} tháng trước"
    else:
        return f"{delta.days // 365} năm trước"



def user_home(request):
    # Lấy 12 truyện mới nhất theo NovelId
    all_novels = Novel.objects.all().order_by("-NovelId")[:12]

    # Lấy 20 truyện mới nhất theo thời gian cập nhật
    novelupdates = Novel.objects.annotate(
        latest_update=Max("chapter__dateUpdate")
    ).order_by("-latest_update")[:20]

    # Lọc ra những truyện có ít nhất một chương
    novelupdates_with_chapters = [novel for novel in novelupdates if novel.chapter_set.exists()]

    # Xử lý dữ liệu cho danh sách truyện mới cập nhật
    for novel in novelupdates_with_chapters:
        latest_chapter = novel.chapter_set.order_by("-dateUpdate").first()
        novel.latest_chapter = latest_chapter  # Gán chương mới nhất

        if latest_chapter:
            novel.latest_update = localtime(latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)

    # Thêm tổng số chương cho mỗi truyện trong all_novels
    for novel in all_novels:
        novel.chapter_count = novel.chapter_set.count()  # Đếm số chương của mỗi truyện

    return render(
        request,
        "novel/User/user_novel_home.html",
        {"all_novels": all_novels, "novelupdates": novelupdates_with_chapters},
    )


def all_novel(request):
    novels_list = Novel.objects.all().order_by(
        "-NovelId"
    )  # Sắp xếp truyện theo NovelId giảm dần
    paginator = Paginator(novels_list, 12)  # Hiển thị 10 truyện mỗi trang

    page_number = request.GET.get("page", 1)  # Lấy số trang từ request, mặc định là 1
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)  # Nếu không phải số nguyên, quay về trang đầu
    except EmptyPage:
        page_obj = paginator.page(
            paginator.num_pages
        )  # Nếu vượt quá số trang, hiển thị trang cuối cùng

    return render(request, "novel/User/all_novel.html", {"page_obj": page_obj})


def user_novel_detail(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)

    # Cập nhật lượt xem, đảm bảo mỗi lần xem chỉ tăng một lần duy nhất cho mỗi user
    if not request.session.get(f"viewed_{novel_id}", False):
        novel.ViewCount += 1
        novel.save()
        request.session[f"viewed_{novel_id}"] = True  # Lưu vào session để tránh tăng nhiều lần

    chapters = Chapter.objects.filter(Novel=novel).order_by("Number")
    chapters_new = Chapter.objects.filter(Novel=novel).order_by("-Number")[:6]
    novel.ChapCount = chapters.count()
    first_chapter = Chapter.objects.filter(Novel=novel).order_by("Number").first()
    first_chapter_id = first_chapter.ChapId if first_chapter else None

    paginator = Paginator(chapters, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    novel123 = Novel.objects.all()[:3]
    novel4_10 = Novel.objects.all()[3:10]

    return render(
        request,
        "novel/User/user_novel_detail.html",
        {
            "novel": novel,
            "chapters": chapters_new,
            "FirstChapterId": first_chapter_id,
            "novels_123": novel123,
            "novels_4_10": novel4_10,
            "page_obj": page_obj,
        },
    )



def user_chapter_detail(request, novel_id, chapter_id):
    chapter = get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id)
    chapters = Chapter.objects.filter(Novel_id=novel_id).order_by("Number")
    novels = Novel.objects.all()
    for novel in novels:
        novel.ChapCount = Chapter.objects.filter(Novel=novel).count()
    return render(
        request,
        "novel/User/user_chapter_detail.html",
        {"chapter": chapter, "chapters": chapters, "novels": novels},
    )

def get_next_chapter(request, novel_id, chapter_id):
    """Lấy chương tiếp theo của truyện"""

    # Lấy chương hiện tại
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()
    print(currentChapter.Number)
    if not currentChapter:
        return JsonResponse(
            {"status": "error", "message": "Không tìm thấy chương này!"}
        )

    # Lấy chương tiếp theo dựa vào Number
    next_chapter = (
        Chapter.objects.filter(Novel_id=novel_id, Number__gt=currentChapter.Number)
        .order_by("Number")
        .first()
    )

    if next_chapter:
        return JsonResponse(
            {"status": "success", "next_chapter_id": next_chapter.ChapId}
        )
    else:
        return JsonResponse({"status": "error", "message": "Đây là chương cuối cùng!"})


def get_prev_chapter(request, novel_id, chapter_id):
    """Lấy chương trước đó của truyện"""
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()
    prev_chapter = (
        Chapter.objects.filter(Novel_id=novel_id, Number__lt=currentChapter.Number)
        .order_by("-Number")
        .first()
    )

    if prev_chapter:
        return JsonResponse(
            {"status": "success", "prev_chapter_id": prev_chapter.ChapId}
        )
    else:
        return JsonResponse({"status": "error", "message": "Đây là chương đầu tiên!"})



def chapter_detail(request, novel_id, chapter_id):
    novel = get_object_or_404(Novel, NovelId=novel_id)
    chapters = Chapter.objects.filter(Novel=novel).order_by(
        "Number"
    )  # Lọc chương theo NovelId
    chapter = get_object_or_404(Chapter, ChapId=chapter_id)

    return render(
        request,
        "novel/user_chapter_detail.html",
        {
            "novel": novel,
            "chapter": chapter,
            "chapters": chapters,  # Danh sách chương thuộc novel_id
        },
    )



def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])  # Mã hóa mật khẩu
            user.is_admin = False  # Đảm bảo không phải admin
            user.save()
            return redirect("login")
    else:
        form = UserRegistrationForm()

    return render(request, "novel/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Tạo một token mới cho mỗi lần đăng nhập
            login_token = str(uuid.uuid4())

            response = redirect("novel_list" if user.is_superuser else "user_home")
            response.set_cookie("login_token", login_token, max_age=3600)  # Hết hạn sau 1 giờ
            
            return response
        else:
            return render(request, "novel/404.html")
    else:
        form = AuthenticationForm()

    return render(request, "novel/login.html", {"form": form})


def logout_view(request):
    response = redirect("user_home")
    response.delete_cookie("login_token")  # Xóa token khi đăng xuất
    logout(request)
    return response

