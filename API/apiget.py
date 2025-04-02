import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime

BASE_URL = 'https://metruyenchu.com.vn'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Tạo thư mục lưu ảnh nếu chưa tồn tại
IMAGE_FOLDER = 'media/novel_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def download_image(img_url, story_name):
    """Tải ảnh về thư mục novel_images/ và trả về đường dẫn tương đối"""
    if not img_url:
        return "No image"
        
    try:
        # Xử lý URL ảnh
        if not img_url.startswith(('http://', 'https://')):  
            img_url = urljoin(BASE_URL, img_url)
            
        # Tạo tên file an toàn
        safe_story_name = "".join(x for x in story_name if x.isalnum() or x in (' ','-','_'))
        safe_story_name = safe_story_name.strip().replace(' ', '_')
        
        # Lấy đuôi file từ URL
        parsed_url = urlparse(img_url)
        img_ext = os.path.splitext(parsed_url.path)[1]
        if not img_ext:
            img_ext = '.jpg'  # Mặc định JPG nếu không có đuôi
        
        img_filename = f"{safe_story_name}{img_ext}"
        img_path = os.path.join(IMAGE_FOLDER, img_filename)  

        # Gửi yêu cầu GET với timeout và verify=False
        response = requests.get(
            img_url, 
            headers=HEADERS, 
            stream=True, 
            timeout=10,
            verify=False
        )
        response.raise_for_status()
        
        # Kiểm tra Content-Type
        if 'image' not in response.headers.get('Content-Type', ''):
            return "Invalid image"
        
        # Lưu ảnh
        with open(img_path, 'wb') as img_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    img_file.write(chunk)
        
        # Chỉ lấy phần "novel_images/..." thay vì "media/novel_images/..."
        relative_path = img_path.replace("media/", "", 1)  # Loại bỏ "media/" nếu có
        relative_path = relative_path.replace("\\", "/")  # Chuyển Windows path thành Unix path nếu cần

        return relative_path

    except Exception as e:
        print(f"Lỗi khi tải ảnh {img_url}: {str(e)}")
        return "Download failed"

def get_stories(start_page=1, end_page=3):
    """ Lấy danh sách truyện từ nhiều trang, nhập trang bắt đầu và trang kết thúc """
    all_stories = []

    for page in range(start_page, end_page + 1):
        if page == 1:
            url = f'{BASE_URL}/danh-sach/truyen-hot'
        else:
            url = f'{BASE_URL}/danh-sach/truyen-hot?page={page}'

        print(f'Đang lấy dữ liệu từ: {url}')
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for index, elem in enumerate(soup.select('.item')):
                title_elem = elem.select_one('h3 a')
                author_elem = elem.select_one('.line a[href^="/tac-gia/"]')
                genre_elem = elem.select_one('.line a[href^="/the-loai/"]')  # Lấy thể loại trực tiếp từ danh sách truyện

                # Lấy số chương từ thẻ .line chứa "Số chương :"
                chapters_elem = elem.select_one('.line span:contains("Số chương :")')
                if chapters_elem:
                    chapters = chapters_elem.get_text(strip=True).split(':')[-1].strip()
                else:
                    chapters = 'Unknown'

                views_elem = elem.select_one('.line span:contains("Lượt xem :")')
                image_elem = elem.select_one('a.cover img')

                if not title_elem:
                    continue

                # Lấy URL truyện
                story_url = title_elem['href']
                if not story_url.startswith('http'):
                    story_url = BASE_URL + story_url
                
                # Lấy tên truyện
                story_name = title_elem.text.strip()

                # Lấy tác giả
                author = author_elem.text.strip() if author_elem else 'Unknown'

                # Lấy thể loại từ trang danh sách
                genre = genre_elem.text.strip() if genre_elem else 'Unknown'

                # Lấy lượt xem
                views = views_elem.text.strip() if views_elem else 'Unknown'

                # Xử lý ảnh
                img_url = image_elem['src'] if image_elem else None
                if img_url and not img_url.startswith(('http://', 'https://')): 
                    img_url = urljoin(BASE_URL, img_url)
                
                # Tải ảnh nếu cần
                img_path = download_image(img_url, story_name)

                story = {
                    'title': story_name,
                    'url': story_url,
                    'author': author,
                    'genre': genre,  # Lưu thể loại trực tiếp từ trang danh sách
                    'chapters': chapters,
                    'views': views,
                    'image_url': img_url,  # Thêm đường dẫn ảnh
                }
                all_stories.append(story)

            time.sleep(1)

        except requests.RequestException as e:
            print(f'Lỗi khi lấy danh sách truyện từ {url}: {e}')
    
    # Lưu tất cả các truyện vào file JSON
    with open('stories.json', 'w', encoding='utf-8') as f:
        json.dump(all_stories, f, ensure_ascii=False, indent=2)
    
    print(f'Đã lưu danh sách {len(all_stories)} truyện vào stories.json')
    get_story_details(all_stories)  # Gọi hàm lấy chi tiết truyện sau khi đã lưu danh sách

    return all_stories  # Trả về danh sách truyện lấy được


# Danh sách thể loại và ID tương ứng
category_mapping = {
    "Huyền Huyễn": 1,
    "Trọng Sinh": 2,
    "Xuyên Không": 4,
    "Khoa Huyễn": 5,
    "Ma Huyễn": 7,
    "Văn Học": 10,
    "Quân Sự": 13,
    "Cổ Đại": 15,
    "Kỳ Ảo": 9,
    "Hài Hước": 14,
    "Tình Cảm": 19,
    "Tâm Lý": 20,
    "Đô Thị": 3,
    "Võng Du": 6,
    "Lịch Sử": 8,
    "Ngôn Tình": 11,
    "Hành Động": 16,
    "Huyền Bí": 17,
    "Kỳ Bí": 18,
    "Tu Tiên": 21,
    "Tiên Hiệp": 24,
    "Đồng Nhân": 27,
    "Cổ Đại": 28,
    "Đam Mỹ": 29,
    "Cơ Trí": 30
}
def get_story_details(stories):
    """Lấy chi tiết mô tả, thể loại và hình ảnh từ lớp 'book' của từng truyện"""
    total_stories = []  # Danh sách chứa thông tin tổng hợp của tất cả truyện
    
    for story in stories:
        url = story['url']
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lấy mô tả và giữ nguyên định dạng HTML gốc
            desc_elem = soup.select_one('.intro')  # Lấy thẻ chứa mô tả
            if desc_elem:
                description = desc_elem.get_text(separator=" ").strip()  # Lấy nội dung văn bản và loại bỏ các ký tự thừa như \r\n
            else:
                description = "Không có mô tả"

            # Lấy hình ảnh từ lớp 'book' (tìm thẻ img bên trong div.book)
            img_elem = soup.select_one('.book-info-pic img')  # Tìm ảnh trong thẻ <img> của div.book
            img_url = img_elem['src'] if img_elem else None
            if img_url and not img_url.startswith(('http://', 'https://')):  # Đảm bảo URL hợp lệ
                img_url = urljoin(BASE_URL, img_url)

            story_name = f"detail_{story['title']}"
            img_path = download_image(img_url, story_name)

            # Tạo giá trị 'date_update' với định dạng chuẩn MongoDB
            date_update = datetime.now().isoformat() + 'Z'  # Định dạng ngày giờ MongoDB

            # Lấy trạng thái truyện (Full hoặc Đang cập nhật)
            status_elem = soup.select_one('span.label-status')
            if status_elem:
                status = status_elem.text.strip()
                if "Full" in status:
                    state = "Hoàn thành"
                elif "Đang cập nhật" in status:
                    state = "Đang tiến hành"
                else:
                    state = "Chưa xác định"
            else:
                state = "Chưa xác định"

            # Lấy thể loại từ thẻ <li class="li--genres">
            genre_elem = soup.select_one('li.li--genres')  # Lấy thẻ <li class="li--genres">
            if genre_elem:
                genres = [genre.text.strip() for genre in genre_elem.find_all('a')]  # Lấy tất cả các <a> trong thẻ <li> và trích xuất tên thể loại
            else:
                genres = ["Chưa xác định"]

            # Chuyển đổi thể loại sang ID
            category_ids = []
            for genre in genres:
                category_id = category_mapping.get(genre, "")
                if category_id:
                    category_ids.append(category_id)

            # Thêm thông tin vào story
            story['description'] = description  # Mô tả dưới dạng văn bản sạch
            story['detailImage'] = img_path  # Lưu đường dẫn ảnh chi tiết
            story['state'] = state  # Trạng thái truyện
            story['genres'] = genres  # Thêm thể loại
            story['category_ids'] = category_ids  # Thêm ID thể loại

            # Thêm vào danh sách tổng hợp
            total_stories.append({
                'Name': story['title'],
                'ViewCount': 0,
                'Description': description,  # Mô tả dưới dạng văn bản
                'Author': story['author'],
                'State': state,  # Trạng thái của truyện (Hoàn thành/Đang tiến hành)
                'ChapCount': 0,
                'ImgUrl': img_path,  # Lưu ảnh chi tiết
                'Categories': category_ids,  # Lưu danh sách ID thể loại (category_ids)
                'dateUpdate': date_update,  # Định dạng ngày tháng theo MongoDB
                'TotalComments': 0
            })

            # Lưu tổng hợp vào file JSON
            with open('total_stories.json', 'w', encoding='utf-8') as f:
                json.dump(total_stories, f, ensure_ascii=False, indent=2)
            print(f'Đã lưu tổng hợp thông tin vào total_stories.json')

            time.sleep(1)

        except requests.RequestException as e:
            print(f'Lỗi khi lấy thông tin từ {url}: {e}')

get_stories(start_page=3, end_page=5)

