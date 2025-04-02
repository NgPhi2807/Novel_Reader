import json
from pymongo import MongoClient

def connect_to_mongodb():
    """Kết nối đến MongoDB và trả về database."""
    client = MongoClient("mongodb+srv://ngphi039:456123nhp@cluster0.jvf7l.mongodb.net/?retryWrites=true&w=majority")
    return client['novel_db']

def get_next_novel_id(collection):
    """Lấy NovelId tiếp theo từ collection novel_novel."""
    last_novel = collection.find_one(sort=[("NovelId", -1)])
    return last_novel['NovelId'] + 1 if last_novel else 1

def get_next_cn_id(collection):
    """Lấy CN_Id tiếp theo từ collection novel_categorynovel."""
    last_entry = collection.find_one(sort=[("CNId", -1)])
    return last_entry['CNId'] + 1 if last_entry else 1

def import_novels_from_json(file_path, novel_collection, categorynovel_collection):
    """Đọc dữ liệu từ file JSON và import vào MongoDB."""
    with open(file_path, 'r', encoding='utf-8') as file:
        stories = json.load(file)
    
    for story in stories:
        story['NovelId'] = get_next_novel_id(novel_collection)
        
        # Lưu tiểu thuyết vào novel_novel
        novel_collection.insert_one({
            "NovelId": story["NovelId"],
            "Name": story["Name"],
            "Description": story["Description"],
            "Author": story["Author"],
            "State": story["State"],
            "ChapCount": story["ChapCount"],
            "ImgUrl": story["ImgUrl"],
            "dateUpdate": story["dateUpdate"],
            "TotalComments": story["TotalComments"],
            "ViewCount": story["ViewCount"],
        })
        
        # Lưu dữ liệu vào novel_categorynovel (tránh trùng lặp)
        for category_id in story.get("Categories", []):
            # Tạo CNId tự động tăng
            cn_id = get_next_cn_id(categorynovel_collection)
            
            # Lưu vào collection novel_categorynovel
            categorynovel_collection.insert_one({
                "CNId": cn_id,
                "Novel_id": story["NovelId"],
                "Category_id": category_id
            })

        print(f"Truyện '{story['Name']}' đã được thêm vào với NovelId: {story['NovelId']}")
    
    print("Đã import tất cả các truyện từ file JSON vào MongoDB.")

if __name__ == "__main__":
    db = connect_to_mongodb()
    novel_novel_collection = db['novel_novel']
    novel_categorynovel_collection = db['novel_categorynovel']
    import_novels_from_json('total_stories.json', novel_novel_collection, novel_categorynovel_collection)
