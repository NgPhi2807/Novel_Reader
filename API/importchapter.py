import json
from pymongo import MongoClient
from datetime import datetime
import random

def connect_to_mongodb():
    """Kết nối đến MongoDB và trả về database."""
    client = MongoClient("mongodb+srv://ngphi039:456123nhp@cluster0.jvf7l.mongodb.net/?retryWrites=true&w=majority")
    return client['novel_db']

def get_random_chap_id(novel_id, db):
    """Tạo ChapId ngẫu nhiên không trùng với các ChapId đã có trong cơ sở dữ liệu."""
    while True:
        chap_id = random.randint(1, 100000)  # Chọn số ngẫu nhiên từ 1 đến 100000 (hoặc giá trị tùy ý)
        if not db.novel_chapter.find_one({"NovelId": novel_id, "ChapId": chap_id}):
            return chap_id

def import_chapters_from_json(file_path, db):
    """Đọc dữ liệu từ file JSON và import vào MongoDB."""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for novel_data in data:
        novel_name = novel_data.get("Name")
        chapters = novel_data.get("chapter", [])

        novel = db.novel_novel.find_one({"Name": novel_name})
        if not novel:
            print(f"Truyện '{novel_name}' không tồn tại trong database.")
            continue

        novel_id = novel["NovelId"]
        for chapter in chapters:
            chap_id = get_random_chap_id(novel_id, db)  # Lấy ChapId ngẫu nhiên không trùng lặp
            chapter_data = {
                "ChapId": chap_id,
                "Novel_id": novel_id,
                "Name": chapter["Name"],
                "Number": chapter["Number"],
                "Content": chapter["Content"],
                "dateUpdate": datetime.strptime(chapter["dateUpdate"], "%Y-%m-%dT%H:%M:%S.%f+00:00")  # Chuyển đổi ngày tháng
            }
            db.novel_chapter.insert_one(chapter_data)
            print(f"Đã thêm Chương {chap_id}: {chapter['Name']}")

    print("Hoàn thành import chương từ file JSON.")

if __name__ == "__main__":
    db = connect_to_mongodb()
    import_chapters_from_json('chapter.json', db)
