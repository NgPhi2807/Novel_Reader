from django import forms
from .models import Novel
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm


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

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên đăng nhập'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mật khẩu'}))