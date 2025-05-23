import os
import sys
import json
from django.db.models import Max
# Thêm đường dẫn chứa thư mục project vào PYTHONPATH
sys.path.append(r'E:\Project\Novel_Reader')

# Đặt biến môi trường trỏ tới settings.py của project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')

import django
django.setup()

from novel.models import Novel, Category, CategoryNovel # Thay 'novel' bằng tên app chứa model Novel nếu khác

def import_novels_from_json(json_path):
    with open(json_path, encoding='utf-8') as f:
        novels = json.load(f)

    max_novel_id = Novel.objects.aggregate(max_id=Max('NovelId'))['max_id'] or 0
    current_id = max_novel_id

    # Lấy max CNId từ bảng CategoryNovel
    max_cnid = CategoryNovel.objects.aggregate(max_cnid=Max('CNId'))['max_cnid'] or 0
    current_cnid = max_cnid

    for novel_data in novels:
        name = novel_data['Name']

        if Novel.objects.filter(Name=name).exists():
            print(f"Truyện '{name}' đã tồn tại, bỏ qua import.")
            continue

        current_id += 1
        novel = Novel.objects.create(
            NovelId=current_id,
            Name=name,
            ViewCount=novel_data.get('ViewCount', 0),
            Description=novel_data.get('Description', ''),
            Author=novel_data.get('Author', ''),
            State=novel_data.get('State', ''),
            ChapCount=novel_data.get('ChapCount', 0),
            ImgUrl=novel_data.get('ImgUrl', ''),
            dateUpdate=novel_data.get('dateUpdate'),
            TotalComments=novel_data.get('TotalComments', 0),
        )

        category_ids = novel_data.get('Categories', [])
        for cat_id in category_ids:
            try:
                category = Category.objects.get(pk=cat_id)
                # Tăng CNId lên 1 trước khi tạo
                current_cnid += 1
                CategoryNovel.objects.create(
                    CNId=current_cnid,
                    Novel=novel,
                    Category=category
                )
            except Category.DoesNotExist:
                print(f"Category với id={cat_id} không tồn tại, bỏ qua.")


if __name__ == '__main__':
    json_path = r"E:\Project\Novel_Reader\API\total_stories.json"  # Đường dẫn tới file json
    import_novels_from_json(json_path)
    print("Import completed!")
