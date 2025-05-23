import requests
import re
import time
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import random

BASE_URL = 'https://metruyenchu.com.vn/'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def get_story_id_and_max_page(html):
    story_id = None
    max_page = 1
    soup = BeautifulSoup(html, 'html.parser')
    paging_div = soup.select_one('div.paging')
    if not paging_div:
        return None, 1
    links = paging_div.find_all('a', onclick=True)
    for a in links:
        onclick = a['onclick']
        m = re.match(r'page\((\d+),(\d+)\)', onclick)
        if m:
            sid = int(m.group(1))
            page_num = int(m.group(2))
            if story_id is None:
                story_id = sid
            if page_num > max_page:
                max_page = page_num
    return story_id, max_page

def get_all_chapters_api(story_id, max_page):
    all_chapters = []
    max_page = min(max_page, 1)  # Giới hạn max_page tối đa là 2
    for page in range(1, max_page + 1):
        api_url = f'{BASE_URL}get/listchap/{story_id}?page={page}'
        print(f"Lấy chương trang {page}/{max_page} từ API: {api_url}")
        resp = requests.get(api_url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        html_content = data.get('data', '')
        soup = BeautifulSoup(html_content, 'html.parser')
        for a in soup.select('a'):
            title = a.text.strip()
            href = a.get('href')
            if not href or href == 'javascript:void(0)':
                continue
            url = urljoin(BASE_URL, href)
            all_chapters.append({'title': title, 'url': url})
        time.sleep(0.3)
    for i, chap in enumerate(all_chapters, 1):
        chap['number'] = i
    return all_chapters

def get_chapters_from_story_url(story_url):
    resp = requests.get(story_url, headers=HEADERS)
    resp.raise_for_status()
    story_id, max_page = get_story_id_and_max_page(resp.text)
    if not story_id:
        print("Không tìm thấy story_id trong trang")
        return []
    print(f"Story ID: {story_id}, Tổng số trang: {max_page}")
    return get_all_chapters_api(story_id, max_page)

def get_chapter_content(chapter_url):
    try:
        response = requests.get(chapter_url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.select_one('.truyen')
        if not content:
            print(f'Không tìm thấy nội dung chương trong {chapter_url}')
            return None
        return content.decode_contents()
    except requests.RequestException as e:
        print(f'Lỗi khi lấy nội dung chương từ {chapter_url}: {e}')
        return None

def get_stories(start_page=1, end_page=2):
    all_stories = []

    for page in range(start_page, end_page + 1):
        url = f'{BASE_URL}danh-sach/truyen-hot' if page == 1 else f'{BASE_URL}danh-sach/truyen-hot?page={page}'
        print(f'Đang lấy dữ liệu từ: {url}')
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            for elem in soup.select('.item'):
                title_elem = elem.select_one('h3 a')
                if not title_elem:
                    continue
                story_url = urljoin(BASE_URL, title_elem['href'])
                story_name = title_elem.text.strip()

                print(f"Lấy chương cho truyện: {story_name}")
                chapters = get_chapters_from_story_url(story_url)

                formatted_chapters = []
                with ThreadPoolExecutor(max_workers=2) as executor:
                    futures = {
                        executor.submit(get_chapter_content, chap['url']): chap for chap in chapters
                    }
                    for future in as_completed(futures):
                        chapter = futures[future]
                        content = future.result()
                        if content:
                            formatted_chapters.append({
                                "Name": chapter["title"],
                                "Number": chapter["number"],
                                "Content": content,
                                "dateUpdate": datetime.now(timezone.utc).isoformat()
                            })

                story = {
                    "Name": story_name,
                    "Chapters": sorted(formatted_chapters, key=lambda x: x["Number"])
                }
                all_stories.append(story)
                time.sleep(random.uniform(0.5, 1.5))


        except requests.RequestException as e:
            print(f'Lỗi khi lấy danh sách truyện từ {url}: {e}')

    with open('get_chapters.json', 'w', encoding='utf-8') as f:
        json.dump(all_stories, f, ensure_ascii=False, indent=2)

    print(f'✅ Đã lưu danh sách {len(all_stories)} truyện vào get_chapters.json')
    return all_stories

if __name__ == "__main__":
    get_stories(start_page=2, end_page=3)
