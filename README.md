# Hệ Thống Quản Lý Tiểu Thuyết

Dự án này là một hệ thống quản lý tiểu thuyết, cho phép bạn tự động lấy dữ liệu tiểu thuyết và chương từ một API bên ngoài và nhập chúng vào cơ sở dữ liệu MySQL cục bộ của bạn. Đây là một công cụ hữu ích để xây dựng một thư viện tiểu thuyết cá nhân hoặc một ứng dụng đọc truyện.

---

## Tính Năng Chính

* **Tích hợp XAMPP/MySQL:** Dễ dàng kết nối với cơ sở dữ liệu MySQL thông qua XAMPP.
* **Lấy dữ liệu tự động:** Tự động tải thông tin tiểu thuyết và chương từ một API được cấu hình sẵn.
* **Nhập dữ liệu vào DB:** Nhập dữ liệu đã lấy vào cơ sở dữ liệu cục bộ của bạn một cách có tổ chức.
* **Hệ thống Django:** Được xây dựng trên framework Django, đảm bảo tính bảo mật và khả năng mở rộng.

---

## Hướng Dẫn Cài Đặt và Sử Dụng

Để bắt đầu với dự án này, hãy làm theo các bước dưới đây.

### 1. Thiết Lập Cơ Sở Dữ Liệu với XAMPP

Trước tiên, bạn cần chuẩn bị cơ sở dữ liệu MySQL sử dụng XAMPP.

1.  **Cài đặt XAMPP:** Nếu chưa có, hãy tải và cài đặt XAMPP từ [trang web chính thức của Apache Friends](https://www.apachefriends.org/index.html).
2.  **Khởi động Apache và MySQL:** Mở **XAMPP Control Panel** và **Start** các module **Apache** và **MySQL**.
3.  **Tạo Cơ Sở Dữ Liệu:**
    * Mở trình duyệt web và truy cập `http://localhost/phpmyadmin`.
    * Trong phpMyAdmin, chọn tab "Databases".
    * Nhập tên cơ sở dữ liệu mới (ví dụ: `novel_db`) vào trường "Create database" và nhấp **Create**.
4.  **Cấu hình Cài đặt Django:**
    * Mở tệp `settings.py` trong thư mục gốc của dự án Django của bạn.
    * Cập nhật phần `DATABASES` để kết nối với cơ sở dữ liệu MySQL của XAMPP:

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'novel_db', # Thay thế bằng tên cơ sở dữ liệu bạn đã tạo
            'USER': 'root',
            'PASSWORD': '', # Để trống nếu không có mật khẩu nào được đặt cho người dùng root XAMPP
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }
    ```
    *Lưu ý: Nếu bạn đã đặt mật khẩu cho người dùng `root` MySQL trong XAMPP, hãy điền mật khẩu đó vào trường `PASSWORD`.*

---

### 2. Thiết Lập Môi Trường Dự Án & Khởi Tạo Cơ Sở Dữ Liệu

Các bước này sẽ tạo môi trường ảo Python, cài đặt các thư viện cần thiết và khởi tạo cấu trúc bảng trong cơ sở dữ liệu.

1.  **Tạo Môi Trường Ảo:**
    python -m venv venv
    
2.  **Kích Hoạt Môi Trường Ảo:**
    * **Trên Windows:**

        venv\Scripts\activate


3.  **Cài Đặt Các Phụ Thuộc:**
    pip install -r requirements.txt

    *Đảm bảo bạn có một file `requirements.txt` trong thư mục gốc của dự án liệt kê tất cả các thư viện cần thiết (ví dụ: `Django`, `mysqlclient`, `requests`).*
4.  **Áp Dụng Các Migration Cơ Sở Dữ Liệu:** Bước này sẽ tạo các bảng cần thiết trong cơ sở dữ liệu `novel_db` của bạn.
    py manage.py makemigrations
    py manage.py migrate

### 3. Thao Tác Dữ Liệu: Lấy và Nhập

Sau khi cấu hình cơ sở dữ liệu, bạn có thể bắt đầu lấy và nhập dữ liệu tiểu thuyết.

1.  **Lấy và Nhập Tiểu Thuyết:**
    * Di chuyển vào thư mục `API`:
        cd API

    * Chạy script để **lấy dữ liệu tiểu thuyết**:
        py getnovels.py

    * Quay lại thư mục dự án chính và vào thư mục ứng dụng `novel`:
        cd ..
        cd novel
 
    * Chạy script để **nhập dữ liệu tiểu thuyết** vào cơ sở dữ liệu của bạn:
        py importnovel.py

2.  **Lấy và Nhập Chương:**
    * Di chuyển trở lại thư mục `API`:
        cd ..
        cd API
     
    * Chạy script để **lấy dữ liệu chương**:
        py getchapters.py
 
    * Quay lại thư mục dự án chính và vào thư mục ứng dụng `novel`:
        cd ..
        cd novel

    * Chạy script để **nhập dữ liệu chương** vào cơ sở dữ liệu của bạn:
        py importchapters.py
 

---

### 4. Chạy Ứng Dụng Django

Cuối cùng, sau khi thiết lập cơ sở dữ liệu và nhập dữ liệu, bạn có thể khởi chạy ứng dụng Django của mình:

py manage.py runserver