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
from rest_framework.views import APIView
from .serializers import NovelSerializer
from .serializers import CategorySerializer
from rest_framework.response import Response
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.utils.timezone import now



from .models import Novel, Category, Chapter, Comment, CustomUser,ReadingProgress,CategoryNovel
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
    
class UserHomeView(APIView):
    def get(self, request):
        all_novels = Novel.objects.all().order_by("-NovelId")[:12]

        novelupdates = Novel.objects.annotate(
            latest_update=Max("chapter__dateUpdate")).order_by("-latest_update")[:20]
        novelupdates_with_chapters = [novel for novel in novelupdates if novel.chapters.exists()]

        all_categories = Category.objects.all()

        for novel in novelupdates_with_chapters:
            latest_chapter = novel.chapters.order_by("-Number").first()
            novel.latest_chapter = latest_chapter

            if latest_chapter:
                novel.latest_update = localtime(latest_chapter.dateUpdate)
                novel.latest_update_display = viet_timesince(novel.latest_update)

        for novel in all_novels:
            novel.chapter_count = novel.chapters.count()

        # Chuyển đổi các đối tượng Novel thành dữ liệu JSON qua serializer
        novels_data = NovelSerializer(all_novels, many=True).data
        novelupdates_data = NovelSerializer(novelupdates_with_chapters, many=True).data

        # Trả về dữ liệu JSON
        return Response({
            "all_novels": novels_data,
            "novelupdates": novelupdates_data,
        })

def user_home(request):
    all_novels = Novel.objects.all().order_by("-NovelId")[:15]
    novel_rank = Novel.objects.all().order_by("-ViewCount")[:10]
    novelupdates = Novel.objects.annotate(
        latest_update=Max("chapters__dateUpdate"),
        chapter_count=Count("chapters")
    ).filter(chapter_count__gt=0).order_by("-latest_update")[:20]

    for novel in novelupdates:
        latest_chapter = novel.chapters.order_by("-dateUpdate").first()
        novel.latest_chapter = latest_chapter

        if latest_chapter:
            novel.latest_update = localtime(latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)

    for novel in all_novels:
        novel.chapter_count = novel.chapters.count()

    all_categories = Category.objects.all()

    return render(
        request,
        "novel/novel_home.html",
        {
            "all_novels": all_novels,
            "novel_rank": novel_rank,
            "novelupdates": novelupdates,
            "all_categories": all_categories,
        },
    )

def all_novel(request):
    novels_list = Novel.objects.all().order_by("-ChapCount", "-NovelId")
    paginator = Paginator(novels_list, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    novels_with_chapters = []
    for novel in page_obj.object_list:
        novel.chapter_count = novel.chapters.count()
        latest_chapters = novel.chapters.order_by("-Number")[:2]
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

    # Lấy reading progress nếu user đã đăng nhập
    if request.user.is_authenticated:
        reading_progress = ReadingProgress.objects.filter(user=request.user, novel=novel).first()
    else:
        reading_progress = None

    paginator = Paginator(chapters, 100)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages

    start_page = ((current_page - 1) // 10) * 10 + 1
    end_page = start_page + 9
    if end_page > total_pages:
        end_page = total_pages

    hot_novels = Novel.objects.all().order_by('-ViewCount')
    novels_123 = hot_novels[:3]
    novels_4_10 = hot_novels[3:10]

    is_following = False
    if request.user.is_authenticated:
        is_following = ReadingProgress.objects.filter(user=request.user, novel=novel).exists()

    comments = Comment.objects.filter(Novel=novel)
    for cmt in comments:
        cmt.time_since = viet_timesince(cmt.CreatedAt)

    novel_categories = novel.categorynovel_set.values_list('Category', flat=True)
    similar_novels = Novel.objects.filter(
        categorynovel__Category__in=novel_categories
    ).exclude(pk=novel.pk).distinct().order_by('-ViewCount')[:12]

    if request.method == 'POST':
        content = request.POST.get('Content', '').strip()
        parent_comment_id = request.POST.get('parent_comment_id')

        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần đăng nhập để bình luận.")
            return redirect('login')

        if content:
            last_comment = Comment.objects.filter(Novel=novel).order_by('-CommentId').first()
            new_comment_id = (last_comment.CommentId + 1) if last_comment else 1

            if parent_comment_id:
                parent_comment = Comment.objects.get(CommentId=parent_comment_id)
                Comment.objects.create(
                    CommentId=new_comment_id,
                    Content=content,
                    User=request.user,
                    Novel=novel,
                    CreatedAt=now(),
                    parent_comment=parent_comment
                )
            else:
                Comment.objects.create(
                    CommentId=new_comment_id,
                    Content=content,
                    User=request.user,
                    Novel=novel,
                    CreatedAt=now(),
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
            "start_page": start_page,
            "end_page": end_page,
            "comments": comments,
            "similar_novels": similar_novels,
            "is_following": is_following,
            "reading_progress": reading_progress,  
        },
    )


def autocomplete_novel(request):
    q = request.GET.get('q', '')
    novels = Novel.objects.filter(Name__icontains=q)[:5]
    results = [
        {
            'NovelId': novel.NovelId,
            'Name': novel.Name,
            'ImgUrl': novel.ImgUrl if novel.ImgUrl else '',
            'Author': novel.Author,
        }
        for novel in novels
    ]
    return JsonResponse(results, safe=False)

def user_chapter_detail(request, novel_id, chapter_id):
    chapter = get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id)
    
    if request.user.is_authenticated:
        ReadingProgress.objects.update_or_create(
            user=request.user,
            novel=chapter.Novel,
            defaults={'current_chapter': chapter}
        )
    
    chapters = Chapter.objects.filter(Novel_id=novel_id).order_by("Number")
    
    novels = Novel.objects.filter(NovelId=novel_id).annotate(chapter_count=Count('chapters'))

    return render(
        request,
        "novel/User/chapter_detail.html",
        {
            "chapter": chapter,
            "chapters": chapters,
            "novels": novels
        },
    )
def get_next_chapter(request, novel_id, chapter_id):
    # Tìm chương hiện tại
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()
    if not currentChapter:
        return JsonResponse({"status": "error", "message": "Không tìm thấy chương này!"})

    # Tìm chương kế tiếp trong cùng một novel
    next_chapter = Chapter.objects.filter(
        Novel_id=novel_id, Number__gt=currentChapter.Number
    ).order_by("Number").first()

    if next_chapter:
        return JsonResponse(
            {"status": "success", "next_chapter_id": next_chapter.ChapId}
        )
    else:
        return JsonResponse({"status": "error", "message": "Đây là chương cuối cùng!"})

def get_prev_chapter(request, novel_id, chapter_id):
    # Tìm chương hiện tại
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()

    # Tìm chương trước trong cùng một novel
    prev_chapter = Chapter.objects.filter(
        Novel_id=novel_id, Number__lt=currentChapter.Number
    ).order_by("-Number").first()

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
    search_query = request.GET.get('search', '').strip()

    novels_list = Novel.objects.all().order_by("-ChapCount", "-NovelId")

    if search_query:
        novels_list = novels_list.filter(Name__icontains=search_query)

    if not novels_list:
        messages.info(request, "Không tìm thấy cuốn tiểu thuyết nào với từ khóa này.")

    paginator = Paginator(novels_list, 12)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    novels_with_chapters = []
    for novel in page_obj.object_list:
        novel.chapter_count = novel.chapters.count()
        latest_chapters = novel.chapters.order_by("-Number")[:2]
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
        "novels_with_chapters": novels_with_chapters,
        "search_query": search_query
    })

def add_comment_reply(request, novel_id):
    if not request.user.is_authenticated:
        messages.error(request, "Bạn cần đăng nhập để bình luận.")
        return redirect('login')

    if request.method == 'POST':
        content = request.POST.get('Content', '').strip()
        parent_comment_id = request.POST.get('parent_comment_id')
        if not content:
            messages.error(request, "Nội dung bình luận không được để trống.")
            return redirect('user_novel_detail', novel_id=novel_id)
        parent_comment = None
        if parent_comment_id:
            try:
                parent_comment = Comment.objects.get(CommentId=parent_comment_id)  # 🔹 Dùng CommentId
            except Comment.DoesNotExist:
                messages.error(request, "Bình luận cha không tồn tại.")
                return redirect('user_novel_detail', novel_id=novel_id)

        new_comment = Comment(
            Content=content,
            User_id=request.user.id,
            Novel_id=novel_id,
            CreatedAt=now(),
            parent_comment_id=parent_comment.CommentId if parent_comment else None
        )
        new_comment.save()

        Novel.objects.filter(id=novel_id).update(TotalComments=Comment.objects.filter(Novel_id=novel_id).count())

        messages.success(request, "Đã thêm bình luận thành công!")
        return redirect('user_novel_detail', novel_id=novel_id)
    return render(request, 'novel/User/novel_detail.html')

@login_required
def theo_doi_truyen(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)
    
    chapter = novel.chapters.order_by('Number').first()  

    if not chapter:
        messages.error(request, "Truyện này chưa có chương nào để theo dõi.")
        return redirect('user_novel_detail', novel_id=novel_id)


    progress, created = ReadingProgress.objects.get_or_create(
        user=request.user,
        novel=novel,
        defaults={'current_chapter': chapter}
    )
    if not created:
        progress.delete()
        message = "Đã hủy theo dõi truyện."
    else:
        messages.success(request, f"Đã theo dõi truyện '{novel.Name}' từ chương đầu tiên.")

    return redirect('user_novel_detail', novel_id=novel_id)

def user_dashboard(request):
    users_count = CustomUser.objects.count()
    novels_count = Novel.objects.count()
    chapters_count = Chapter.objects.count()

    context = {
        "users_count": users_count,
        "novels_count": novels_count,
        "chapters_count": chapters_count,
    }

    return render(request, "novel/user/novel_followed.html", context)

@login_required
def novels_followed(request):
    progresses = ReadingProgress.objects.filter(user=request.user).select_related('novel')
    novel_ids = progresses.values_list('novel__NovelId', flat=True)

    novels = (
        Novel.objects
        .filter(NovelId__in=novel_ids)
        .annotate(ChapterCount=Count('chapters')) 
    )

    return render(request, 'novel/user/novel_followed.html', {
        'novels': novels,
    })

@login_required
def unfollow_novel(request, novel_id):
    try:
        progress = ReadingProgress.objects.get(user=request.user, novel_id=novel_id)
        progress.delete()
        return JsonResponse({'success': True, 'message': 'Bỏ theo dõi thành công!'})
    except ReadingProgress.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy truyện trong danh sách theo dõi!'})
    
def novel_category(request, category_id):
    the_loai = get_object_or_404(Category, pk=category_id)
    category_novel_qs = CategoryNovel.objects.select_related('Novel').filter(Category=the_loai)
    novels = [cn.Novel for cn in category_novel_qs]

    # Phân trang
    paginator = Paginator(novels, 6)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'novel/user/novel_category.html', {
        'the_loai': the_loai,
        'page_obj': page_obj,
    })