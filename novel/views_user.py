from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Max
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import localtime, now
from datetime import timedelta
import random

from .models import Novel, Category, Chapter, Comment, CustomUser
from .forms import PasswordResetRequestForm
from django.contrib.auth import get_user_model

User = get_user_model()

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
    all_novels = Novel.objects.all().order_by("-NovelId")[:12]
    novelupdates = Novel.objects.annotate(
        latest_update=Max("chapter__dateUpdate")).order_by("-latest_update")[:20]
    novelupdates_with_chapters = [novel for novel in novelupdates if novel.chapter_set.exists()]

    for novel in novelupdates_with_chapters:
        latest_chapter = novel.chapter_set.order_by("-dateUpdate").first()
        novel.latest_chapter = latest_chapter

        if latest_chapter:
            novel.latest_update = localtime(latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)

    for novel in all_novels:
        novel.chapter_count = novel.chapter_set.count()

    return render(
        request,
        "novel/novel_home.html",
        {"all_novels": all_novels,
        "novelupdates": novelupdates_with_chapters},
    )

def all_novel(request):
    novels_list = Novel.objects.all().order_by("-ChapCount", "-NovelId")
    paginator = Paginator(novels_list, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    novels_with_chapters = []
    for novel in page_obj.object_list:
        novel.chapter_count = novel.chapter_set.count()
        latest_chapters = novel.chapter_set.order_by("-ChapId")[:2]
        novel.latest_chapters = latest_chapters

        if latest_chapters:
            novel.latest_chapter = latest_chapters[0]
            novel.latest_update = localtime(novel.latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)
        else:
            novel.latest_update_display = "Chưa có chương nào cập nhật"

        novels_with_chapters.append(novel)

    return render(request, "novel/User/all_novel.html", {
        "page_obj": page_obj,
        "novels_with_chapters": novels_with_chapters
    })

def user_novel_detail(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)

    if not request.session.get(f"viewed_{novel_id}", False):
        novel.ViewCount += 1
        novel.save()
        request.session[f"viewed_{novel_id}"] = True

    chapters = Chapter.objects.filter(Novel=novel).order_by("Number")
    chapters_new = Chapter.objects.filter(Novel=novel).order_by("-Number")[:6]
    novel.ChapCount = chapters.count()
    first_chapter = Chapter.objects.filter(Novel=novel).order_by("Number").first()
    first_chapter_id = first_chapter.ChapId if first_chapter else None

    paginator = Paginator(chapters, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    hot_novels = Novel.objects.all().order_by('-ViewCount')
    novels_123 = hot_novels[:3]
    novels_4_10 = hot_novels[3:10]

    comments = Comment.objects.filter(Novel=novel).order_by('-CreatedAt')

    for cmt in comments:
        cmt.time_since = viet_timesince(cmt.CreatedAt)

    if request.method == 'POST':
        content = request.POST.get('Content', '').strip()

        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để bình luận.")
            return redirect('login')

        if content:
            Comment.objects.create(
                Content=content,
                User=request.user,
                Novel=novel,
                CreatedAt=now()
            )

            novel.TotalComments = Comment.objects.filter(Novel=novel).count()
            novel.save()

            messages.success(request, "Đã thêm bình luận thành công!")
            return redirect('user_novel_detail', novel_id=novel_id)
        else:
            messages.error(request, "Nội dung bình luận không được để trống.")

    return render(
        request,
        "novel/User/novel_detail.html",
        {
            "novel": novel,
            "chapters": chapters_new,
            "FirstChapterId": first_chapter_id,
            "novels_123": novels_123,
            "novels_4_10": novels_4_10,
            "page_obj": page_obj,
            "comments": comments,
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
        "novel/User/chapter_detail.html",
        {"chapter": chapter, "chapters": chapters, "novels": novels},
    )

def get_next_chapter(request, novel_id, chapter_id):
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()
    if not currentChapter:
        return JsonResponse(
            {"status": "error", "message": "Không tìm thấy chương này!"}
        )

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

@csrf_exempt
def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        email = request.POST.get("email")
        sdt = request.POST.get("sdt")

        errors = []

        if not username or not password or not email or not sdt:
            errors.append("Vui lòng nhập đầy đủ thông tin.")

        if CustomUser.objects.filter(username=username).exists():
            errors.append("Tên tài khoản đã tồn tại.")

        if CustomUser.objects.filter(email=email).exists():
            errors.append("Email đã được sử dụng.")

        if CustomUser.objects.filter(sdt=sdt).exists():
            errors.append("Số điện thoại đã được sử dụng.")

        if errors:
            return JsonResponse({"success": False, "messages": errors})

        user = CustomUser(username=username, email=email, sdt=sdt)
        user.set_password(password)
        user.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "messages": ["Phương thức không hợp lệ."]})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                "success": True,
                "is_admin": user.is_superuser
            })
        else:
            return JsonResponse({
                "success": False,
                "messages": ["Tên đăng nhập hoặc mật khẩu không đúng!"]
            })
    return JsonResponse({"success": False, "messages": ["Yêu cầu không hợp lệ."]})

def logout_view(request):
    logout(request)
    return redirect("user_home")

def generate_reset_code():
    return str(random.randint(100000, 999999))

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]

            if not User.objects.filter(email=email).exists():
                return JsonResponse({"success": False, "messages": ["Email này không tồn tại trong hệ thống."]})

            last_sent_time = request.session.get("reset_last_sent_time")
            if last_sent_time:
                last_sent_time = now() - timedelta(seconds=60)
                if now() < last_sent_time:
                    return JsonResponse({"success": False, "messages": ["Vui lòng chờ 60 giây trước khi gửi lại."]})

            reset_code = generate_reset_code()
            send_mail(
                "Mã xác nhận đặt lại mật khẩu",
                f"Mã xác nhận của bạn là: {reset_code}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )

            request.session["reset_code"] = reset_code
            request.session["reset_email"] = email
            request.session["reset_last_sent_time"] = now().isoformat()

            return JsonResponse({"success": True, "message": "Mã xác nhận đã được gửi qua email."})

        return JsonResponse({"success": False, "messages": form.errors.get("email", ["Email không hợp lệ."])})

    return JsonResponse({"success": False, "messages": ["Phương thức không hợp lệ."]})

def password_reset_verify(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        reset_code = request.session.get("reset_code")

        if not reset_code:
            return JsonResponse({
                "success": False, 
                "message": "Mã xác nhận đã hết hạn hoặc không hợp lệ. Vui lòng yêu cầu mã mới."
            })

        if reset_code == code:
            del request.session["reset_code"]
            return JsonResponse({
                "success": True,
                "message": "Xác nhận thành công"
            })

        return JsonResponse({
            "success": False, 
            "message": "Mã xác nhận không đúng. Vui lòng kiểm tra và thử lại."
        })

def password_reset_confirm(request):
    email = request.session.get("reset_email")
    if not email:
        return JsonResponse({"success": False, "message": "Phiên đặt lại mật khẩu đã hết hạn. Vui lòng thử lại."})

    new_password = request.POST.get("new_password", "").strip()
    
    if not new_password:
        return JsonResponse({"success": False, "message": "Mật khẩu mới không được để trống."})

    try:
        user = User.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()

        del request.session["reset_email"]

        return JsonResponse({"success": True, "message": "Mật khẩu đã được đặt lại thành công!"})

    except User.DoesNotExist:
        return JsonResponse({"success": False, "message": "Không tìm thấy tài khoản!"})
    
def search_novel(request):
    novels_list = Novel.objects.all().order_by("-ChapCount", "-NovelId")
    paginator = Paginator(novels_list, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    novels_with_chapters = []
    for novel in page_obj.object_list:
        novel.chapter_count = novel.chapter_set.count()
        latest_chapters = novel.chapter_set.order_by("-ChapId")[:2]
        novel.latest_chapters = latest_chapters

        if latest_chapters:
            novel.latest_chapter = latest_chapters[0]
            novel.latest_update = localtime(novel.latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)
        else:
            novel.latest_update_display = "Chưa có chương nào cập nhật"

        novels_with_chapters.append(novel)

    return render(request, "novel/User/search_novel.html", {
        "page_obj": page_obj,
        "novels_with_chapters": novels_with_chapters
    })