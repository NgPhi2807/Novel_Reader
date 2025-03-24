from django.shortcuts import render, get_object_or_404, redirect
from .models import Novel, Category, CategoryNovel, Chapter
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.http import require_POST
from django.db.models import Max  # Thêm dòng này
from django.utils.timezone import localtime
from django.utils.timezone import now, localtime
from datetime import timedelta




def novel_list(request):
    novels = Novel.objects.all()
    return render(request, "novel/novel_list.html", {"novels": novels})


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


# def add_novel(request):
#     if request.method == 'POST':
#         name = request.POST.get("name")
#         description = request.POST.get("description")
#         author = request.POST.get("author")
#         state = request.POST.get("state")
#         chap_count = 0
#         img = request.FILES.get("img")
#         category_ids = request.POST.getlist('categories')

#         novel = Novel(
#             Name=name,
#             Description=description,
#             Author=author,
#             State=state,
#             ChapCount=int(chap_count) if chap_count else 0,
#         )
#
#         if img:
#             novel.ImgUrl = img
#         novel.save()
#         for category_id in category_ids:
#             category = Category.objects.get(pk=category_id)
#             CategoryNovel.objects.create(Novel=novel, Category=category)
#         return redirect("novel_list")
#     categories = Category.objects.all()
#     return render(request, 'novel/novel_create.html', {'categories': categories})



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

def list_chapter(request, novel_id):

    novel = get_object_or_404(Novel, pk=novel_id)
    chapters = Chapter.objects.filter(Novel=novel).order_by('Number') 
    if request.method == "POST":
        name = request.POST.get('name')
        number = request.POST.get('number')
        content = request.POST.get('content')

        if name and number and content:  # Kiểm tra dữ liệu hợp lệ
            Chapter.objects.create(
                Novel=novel,
                Name=name,
                Number=number,
                Content=content
            )
            return redirect('novel_list')  # Chuyển về trang chi tiết truyện


    return render(request, 'novel/chapter_add.html', {'novel': novel, 'chapters' : chapters})

####   USER
def user_home(request):
    novelupdates = Novel.objects.annotate(
        latest_update=Max('chapter__dateUpdate')  # Lấy thời gian cập nhật chương mới nhất
    ).order_by('-latest_update')  # Sắp xếp theo chương mới nhất

    # Lấy danh sách chương theo số chương cho mỗi tiểu thuyết
    for novel in novelupdates:
        novel.chapters = novel.chapter_set.all().order_by('Number')

        # Lấy chương mới nhất của từng novel
        latest_chapter = novel.chapter_set.order_by('-dateUpdate').first()
        novel.latest_chapter = latest_chapter  # Gán chương mới nhất cho tiểu thuyết đó

        # Format lại thời gian cập nhật theo múi giờ Việt Nam
        if latest_chapter:
            novel.latest_update = localtime(latest_chapter.dateUpdate)
            novel.latest_update_display = viet_timesince(novel.latest_update)

    return render(request, 'novel/User/user_novel_home.html', {'novels': novelupdates})

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

def user_novel_detail(request, novel_id):
    novel = get_object_or_404(Novel, pk=novel_id)
    chapters = Chapter.objects.filter(Novel=novel).order_by('Number')  
    novel.ChapCount = chapters.count()  
    first_chapter = Chapter.objects.filter(Novel=novel).order_by('Number').first()
    first_chapter_id = first_chapter.ChapId if first_chapter else None
    
    # Lấy các tiểu thuyết từ vị trí 1 đến 3
    novel123 = Novel.objects.all()[:3]
    
    # Lấy các tiểu thuyết từ vị trí 4 đến 10
    novel4_10 = Novel.objects.all()[3:10]

    return render(request, 'novel/User/user_novel_detail.html', {
        'novel': novel, 
        'chapters': chapters,
        'FirstChapterId': first_chapter_id, 
        'novels_123': novel123,  # Đặt tên rõ ràng cho biến
        'novels_4_10': novel4_10,  # Đặt tên rõ ràng cho biến
    })



def user_chapter_detail(request, novel_id, chapter_id):
        chapter = get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id)
        chapters = Chapter.objects.filter(Novel_id=novel_id).order_by('Number')
        novels = Novel.objects.all()
        for novel in novels:
            novel.ChapCount = Chapter.objects.filter(Novel=novel).count() 
        return render(request, 'novel/User/user_chapter_detail.html', {'chapter': chapter,
                                                                        'chapters': chapters, 'novels': novels}) 

def get_chapter(request, novel_id, chapter_id):
    chapter = get_object_or_404(Chapter, ChapId=chapter_id, Novel_id=novel_id),
    return JsonResponse({"name": chapter.Name, "content": chapter.Content})

def get_next_chapter(request, novel_id, chapter_id):
    """Lấy chương tiếp theo của truyện"""

    # Lấy chương hiện tại
    currentChapter = Chapter.objects.filter(ChapId=chapter_id).first()
    print(currentChapter.Number)
    if not currentChapter:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy chương này!'})

    # Lấy chương tiếp theo dựa vào Number
    next_chapter = Chapter.objects.filter(Novel_id=novel_id, Number__gt=currentChapter.Number).order_by('Number').first()
    
    if next_chapter:
        return JsonResponse({'status': 'success', 'next_chapter_id': next_chapter.ChapId})
    else:
        return JsonResponse({'status': 'error', 'message': 'Đây là chương cuối cùng!'})

def get_prev_chapter(request, novel_id, chapter_id):
    """Lấy chương trước đó của truyện"""
    currentChapter = Chapter.objects.filter(ChapId = chapter_id).first()
    prev_chapter = Chapter.objects.filter(Novel_id=novel_id, Number__lt=currentChapter.Number).order_by('-Number').first()
    
    if prev_chapter:
        return JsonResponse({'status': 'success', 'prev_chapter_id': prev_chapter.ChapId})
    else:
        return JsonResponse({'status': 'error', 'message': 'Đây là chương đầu tiên!'})


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
            return JsonResponse({"status": "error", "message": "Không tìm thấy chương!"}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Dữ liệu không hợp lệ!"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Chỉ hỗ trợ POST!"}, status=405)


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

        chapter = Chapter.objects.create(
            Novel=novel,
            Name=name,
            Number=number,
            Content=content
        )

        return JsonResponse({
            'status': 'success',
            'message': 'Thêm chương thành công',
            'chapter_id': chapter.ChapId
        })
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Dữ liệu không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)    
    
@csrf_exempt
@require_POST
def delete_chapter(request, novel_id, chap_id):
    try:
        # Lấy chapter dựa trên chap_id và novel_id
        chapter = get_object_or_404(Chapter, ChapId=chap_id, Novel__NovelId=novel_id)
        chapter.delete()  # Xóa chapter khỏi database
        
        return JsonResponse({
            'status': 'success',
            'message': 'Xóa chương thành công'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def chapter_detail(request, novel_id, chapter_id):
    novel = get_object_or_404(Novel, NovelId=novel_id)
    chapters = Chapter.objects.filter(Novel=novel).order_by('Number')  # Lọc chương theo NovelId
    chapter = get_object_or_404(Chapter, ChapId=chapter_id)

    return render(request, 'novel/user_chapter_detail.html', {
        'novel': novel,
        'chapter': chapter,
        'chapters': chapters,  # Danh sách chương thuộc novel_id
    })
