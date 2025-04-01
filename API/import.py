import json
from pymongo import MongoClient

# Kết nối đến MongoDB
client = MongoClient("mongodb+srv://ngphi039:456123nhp@cluster0.jvf7l.mongodb.net/?retryWrites=true&w=majority")
db = client['novel_db']

# Chọn collection novel_novel
novel_novel_collection = db['novel_novel']

# Hàm lấy NovelId tiếp theo
def get_next_novel_id():
    # Tìm NovelId lớn nhất trong collection novel_novel
    last_novel = novel_novel_collection.find_one(sort=[("NovelId", -1)])
    if last_novel:
        return last_novel['NovelId'] + 1  # Tăng lên 1 so với NovelId cuối cùng
    else:
        return 1  # Nếu không có truyện nào, bắt đầu từ 1

# Đọc dữ liệu từ file JSON
with open('total_stories.json', 'r', encoding='utf-8') as file:
    stories = json.load(file)

# Import từng truyện vào MongoDB
for story in stories:
    # Lấy NovelId tiếp theo
    story['NovelId'] = get_next_novel_id()

    # Insert truyện vào MongoDB (collection novel_novel)
    novel_novel_collection.insert_one(story)

    print(f"Truyện '{story['Name']}' đã được thêm vào với NovelId: {story['NovelId']}")

print("Đã import tất cả các truyện từ file JSON vào MongoDB (collection novel_novel).")
