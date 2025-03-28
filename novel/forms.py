from django import forms
from .models import Novel
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()

class NovelForm(forms.ModelForm):
    class Meta:
        model = Novel
        fields = ['Name', 'Author', 'Description', 'ImgUrl']  # Thêm Img

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mật khẩu")

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'sdt']
        labels = {
            'username': 'Tài khoản',
            'email': 'Email',
            'sdt': 'Số điện thoại',
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            raise forms.ValidationError("Mật khẩu không được để trống.")
        return password
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254, required=True)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này không tồn tại trong hệ thống.")
        return email    
class PasswordResetVerifyForm(forms.Form):
    code = forms.CharField(label="Mã xác nhận", max_length=6, required=True)