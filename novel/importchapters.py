import os
import sys
import json
from django.utils.dateparse import parse_datetime

# Đặt đường dẫn dự án và cấu hình môi trường Django
sys.path.append(r'E:\Project\Novel_Reader')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_project.settings')

import django
django.setup()

from novel.models import Novel, Chapter

def import_chapters_from_json(json_path):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    # Lấy tất cả truyện trong DB và lưu vào dict {tên truyện: Novel instance}
    novel_dict = {novel.Name: novel for novel in Novel.objects.all()}

    for novel_data in data:
        novel_name = novel_data.get('Name')
        if not novel_name:
            print("Truyện không có tên, bỏ qua.")
            continue

        novel = novel_dict.get(novel_name)
        if not novel:
            print(f"Không tìm thấy truyện trong DB: {novel_name}")
            continue

        chapters = novel_data.get('Chapters', [])  # Đổi 'chapter' thành 'Chapters' nếu đúng key trong JSON
        for chap_data in chapters:
            number = chap_data.get('Number')
            name = chap_data.get('Name')
            content = chap_data.get('Content', '')
            date_update = chap_data.get('dateUpdate', None)

            if not number or not name:
                print(f"Bỏ qua chương thiếu thông tin trong truyện: {novel_name}")
                continue

            defaults = {
                'Name': name,
                'Content': content,
            }

            if date_update:
                parsed_date = parse_datetime(date_update)
                if parsed_date:
                    defaults['dateUpdate'] = parsed_date

            chapter, created = Chapter.objects.update_or_create(
                Novel=novel,
                Number=number,
                defaults=defaults
            )

            action = "Thêm" if created else "Cập nhật"
            print(f"{action} chương {number} - {name} cho truyện '{novel_name}'.")

if __name__ == '__main__':
    json_path = r"E:\Project\Novel_Reader\Crawler\get_chapters.json"  # File JSON chứa chương
    import_chapters_from_json(json_path)
    print("Import chương hoàn tất!")
