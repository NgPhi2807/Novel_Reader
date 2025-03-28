from datetime import timedelta
from django.shortcuts import redirect
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime
from django.contrib.auth import logout

class AutoLogoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        last_active = request.COOKIES.get("last_active")

        if last_active:
            last_active_time = parse_datetime(last_active)  # Tự động nhận diện định dạng ISO 8601

            if last_active_time is None:  # Nếu cookie bị lỗi định dạng
                return self.get_response(request)

            # Kiểm tra nếu đã quá 30 phút
            if now() - last_active_time > timedelta(minutes=30):
                response = redirect("login")
                response.delete_cookie("login_token")
                response.delete_cookie("last_active")
                logout(request)  # Đăng xuất user
                return response

        return self.get_response(request)
