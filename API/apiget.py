import os
import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import urllib3
from datetime import datetime

BASE_URL = 'https://truyenfull.vision'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Tạo thư mục lưu ảnh nếu chưa tồn tại
IMAGE_FOLDER = 'media/novel_images'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Thêm xử lý cảnh báo SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_image(img_url, story_name):
    """Tải ảnh về thư mục media/novel_images/ và trả về đường dẫn tương đối"""
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

    
def get_stories(page_limit=3):
    """ Lấy danh sách truyện từ nhiều trang """
    all_stories = []
    
    for page in range(1, page_limit + 1):
        url = f'{BASE_URL}/danh-sach/truyen-moi/trang-{page}/'
        print(f'Đang lấy dữ liệu từ: {url}')
        
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for index, elem in enumerate(soup.select('.list-truyen .row')):
                title_elem = elem.select_one('.truyen-title a')
                author_elem = elem.select_one('.author')
                chapupdate_elem = elem.select_one('.text-info')
                image_elem = elem.select_one('.col-xs-3 img.cover')

                if not title_elem:
                    continue

                story_url = title_elem['href']
                if not story_url.startswith('http'):
                    story_url = BASE_URL + story_url

                # Xử lý URL ảnh
                img_url = image_elem['src'] if image_elem else None
                if img_url and not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(BASE_URL, img_url)
                
                story_name = f"{title_elem.text.strip()}_{page}_{index}"  # Thêm page và index để tránh trùng tên
                img_path = download_image(img_url, story_name)

                story = {
                    'title': title_elem.text.strip(),
                    'url': story_url,
                    'author': author_elem.text.strip() if author_elem else 'Unknown',
                    'Chapupdate': chapupdate_elem.text.strip() if chapupdate_elem else 'N/A',
                    'authorImage': img_path  # Lưu đường dẫn ảnh đã tải về
                }
                all_stories.append(story)

            time.sleep(1)

        except requests.RequestException as e:
            print(f'Lỗi khi lấy danh sách truyện từ {url}: {e}')
    
    # Lưu tất cả các truyện vào file JSON
    with open('stories.json', 'w', encoding='utf-8') as f:
        json.dump(all_stories, f, ensure_ascii=False, indent=2)
    
    print(f'Đã lưu danh sách {len(all_stories)} truyện vào stories.json')
    get_story_details(all_stories)

def get_story_details(stories):
    """Lấy chi tiết mô tả, thể loại và hình ảnh từ lớp 'book' của từng truyện"""
    total_stories = []  # Danh sách chứa thông tin tổng hợp của tất cả truyện
    id_counter = 1  # Khởi tạo biến đếm ID tự tăng
    
    for story in stories:
        url = story['url']
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lấy thể loại từ class cha "info"
            genre_parent = soup.select_one('.info')
            genres = [a.text.strip() for a in genre_parent.select('a[itemprop="genre"]')] if genre_parent else []

            # Lấy mô tả
            desc_elem = soup.select_one('.desc-text')
            description = desc_elem.text.strip() if desc_elem else "Không có mô tả"

            # Lấy hình ảnh từ lớp 'book' (tìm thẻ img bên trong div.book)
            img_elem = soup.select_one('.book img')  # Tìm ảnh trong thẻ <img> của div.book
            img_url = img_elem['src'] if img_elem else None
            if img_url and not img_url.startswith(('http://', 'https://')):  # Đảm bảo URL hợp lệ
                img_url = urljoin(BASE_URL, img_url)
            
            story_name = f"detail_{story['title']}"
            img_path = download_image(img_url, story_name)

            # Tạo giá trị 'date_update' với định dạng chuẩn MongoDB
            date_update = datetime.now().isoformat() + 'Z'  # Định dạng ngày giờ MongoDB

            # Thêm thông tin vào story
            story['genres'] = genres
            story['description'] = description
            story['detailImage'] = img_path  # Lưu đường dẫn ảnh chi tiết

            # Thêm vào danh sách tổng hợp với id tự tăng
            total_stories.append({
                'Name': story['title'],
                'ViewCount': 0,
                'Description': description,
                'Author': story['author'],
                'State': 'Đang ra',
                'ChapCount': 0,
                'ImgUrl': img_path,  # Lưu ảnh chi tiết
                'dateUpdate': {"$date": date_update},  # Định dạng ngày tháng theo MongoDB
                'TotalComments': 0
            })

            # Tăng ID cho truyện tiếp theo
            id_counter += 1

            # Lưu mỗi truyện vào file riêng
            story_name = url.split('/')[-1]
            with open(f'story-{story_name}.json', 'w', encoding='utf-8') as f:
                json.dump(story, f, ensure_ascii=False, indent=2)
            print(f'Đã lưu chi tiết: story-{story_name}.json')

            time.sleep(1)

        except requests.RequestException as e:
            print(f'Lỗi khi lấy thông tin từ {url}: {e}')

    # Lưu tất cả thông tin vào một tệp tổng hợp
    with open('total_stories.json', 'w', encoding='utf-8') as f:
        json.dump(total_stories, f, ensure_ascii=False, indent=2)
    
    print(f'Đã lưu tổng hợp thông tin của {len(total_stories)} truyện vào total_stories.json')
get_stories(page_limit=1)
