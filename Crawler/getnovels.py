import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = 'https://metruyenchu.com.vn'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Danh sách thể loại và ID tương ứng
category_mapping = {
    "Tiên Hiệp": 16, "Võng Du": 17, "Huyền Huyễn": 18, "Quân Sự": 19, "Xuyên Nhanh": 20,
    "Linh Dị": 21, "Sủng": 22, "Gia Đấu": 23, "Điền Văn": 24, "Nữ Phụ": 25, "Hiện Đại": 26,
    "Kiếm Hiệp": 27, "Khoa Huyễn": 28, "Dị Giới": 29, "Lịch Sử": 30, "Trọng Sinh": 31,
    "Ngược": 32, "Cung Đấu": 33, "Đông Phương": 34, "Mạt Thế": 35, "Ngôn Tình": 36,
    "Quan Trường": 37, "Hệ Thống": 38, "Dị Năng": 39, "Xuyên Không": 40, "Trinh Thám": 41,
    "Sắc": 42, "Nữ Cường": 43, "Đô Thị": 44, "Truyện Teen": 45, "Đoản Văn": 46
}

def fetch_story_detail(story):
    url = story['url']
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        description_elem = soup.select_one('.intro')
        description = description_elem.get_text(separator=" ").strip() if description_elem else "Không có mô tả"

        img_elem = soup.select_one('.book-info-pic img')
        img_url = img_elem['src'] if img_elem else story['image_url']
        if img_url and not img_url.startswith(('http://', 'https://')):
            img_url = urljoin(BASE_URL, img_url)

        date_update = datetime.now().isoformat() + 'Z'

        # Trạng thái
        status_elem = soup.select_one('span.label-status')
        if status_elem:
            text = status_elem.text.strip()
            if "Full" in text:
                state = "Hoàn thành"
            elif "Đang cập nhật" in text:
                state = "Đang tiến hành"
            else:
                state = "Chưa xác định"
        else:
            state = "Chưa xác định"

        # Thể loại
        genre_elem = soup.select_one('li.li--genres')
        genres = [g.text.strip() for g in genre_elem.find_all('a')] if genre_elem else ["Chưa xác định"]
        category_ids = [category_mapping.get(g, "") for g in genres if g in category_mapping]

        # Số chương
        chap_count = 0
        for li in soup.select('li'):
            if "Số chương" in li.text:
                match = re.search(r"Số chương\s*:\s*(\d+)", li.text)
                if match:
                    chap_count = int(match.group(1))
                break

        # View count
        view_count = 0
        if story['views'] != 'Unknown':
            try:
                view_count = int(story['views'].replace(',', '').replace('.', ''))
            except:
                pass

        return {
            'Name': story['title'],
            'Description': description,
            'Author': story['author'],
            'State': state,
            'ChapCount': chap_count,
            'ImgUrl': img_url,
            'Categories': category_ids,
            'dateUpdate': date_update,
            'ViewCount': view_count,
            'TotalComments': 0
        }

    except requests.RequestException as e:
        print(f'❌ Lỗi khi lấy thông tin từ {url}: {e}')
        return None

def get_story_details(stories):
    total_stories = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_story_detail, story) for story in stories]
        for future in as_completed(futures):
            result = future.result()
            if result:
                total_stories.append(result)

    with open('total_stories.json', 'w', encoding='utf-8') as f:
        json.dump(total_stories, f, ensure_ascii=False, indent=2)

    print(f'✅ Đã lưu {len(total_stories)} truyện vào total_stories.json')
    return total_stories

def get_stories(start_page=1, end_page=2):
    all_stories = []

    for page in range(start_page, end_page + 1):
        url = f'{BASE_URL}/danh-sach/truyen-hot' if page == 1 else f'{BASE_URL}/danh-sach/truyen-hot?page={page}'
        print(f'🔍 Đang lấy dữ liệu từ: {url}')

        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for elem in soup.select('.item'):
                title_elem = elem.select_one('h3 a')
                if not title_elem:
                    continue

                story_name = title_elem.text.strip()
                story_url = urljoin(BASE_URL, title_elem['href'])

                author_elem = elem.select_one('.line a[href^="/tac-gia/"]')
                author = author_elem.text.strip() if author_elem else 'Unknown'

                genre_elem = elem.select_one('.line a[href^="/the-loai/"]')
                genre = genre_elem.text.strip() if genre_elem else 'Unknown'

                image_elem = elem.select_one('a.cover img')
                img_url = image_elem['src'] if image_elem else None
                if img_url and not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(BASE_URL, img_url)

                chapters = 'Unknown'
                views = 'Unknown'
                for span in elem.select('.line span'):
                    if "Số chương :" in span.text:
                        chapters = span.text.split(':')[-1].strip()
                    elif "Lượt xem :" in span.text:
                        views = span.text.split(':')[-1].strip()

                story = {
                    'title': story_name,
                    'url': story_url,
                    'author': author,
                    'genre': genre,
                    'chapters': chapters,
                    'views': views,
                    'image_url': img_url,
                }
                all_stories.append(story)

            time.sleep(1)

        except requests.RequestException as e:
            print(f'❌ Lỗi khi lấy trang {url}: {e}')

    return get_story_details(all_stories)

if __name__ == "__main__":
    get_stories(start_page=1, end_page=2)
