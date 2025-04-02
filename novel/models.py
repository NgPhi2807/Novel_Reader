from django.db import models
from django.contrib.auth.models import AbstractUser
from djongo import models
from django.contrib.auth import get_user_model

class CustomUser(AbstractUser):
    sdt = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")  
    is_admin = models.BooleanField(default=False, verbose_name="Là Admin")  

    def __str__(self):
        return self.username

class Novel(models.Model):
    NovelId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)
    ViewCount = models.IntegerField(default=0)
    Description = models.TextField()
    Author = models.CharField(max_length=255)
    State = models.CharField(max_length=50)
    ChapCount = models.IntegerField(default=0)
    ImgUrl = models.ImageField(upload_to='novel_images/')
    dateUpdate = models.DateTimeField(auto_now=True)
    TotalComments = models.IntegerField(default=0)

class Chapter(models.Model):
    ChapId = models.AutoField(primary_key=True)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    Name = models.CharField(max_length=255)
    Number = models.IntegerField()
    Content = models.TextField()
    dateUpdate = models.DateTimeField(auto_now=True)


class Category(models.Model):
    CategoryId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)

class CategoryNovel(models.Model):
    CNId = models.AutoField(primary_key=True)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)

class User(models.Model):
    UserId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Cần mã hóa mật khẩu

class UserNovel(models.Model):
    UNId = models.AutoField(primary_key=True)
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)


class Comment(models.Model):
    CommentId = models.IntegerField()
    Content = models.TextField()
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    CreatedAt = models.DateTimeField()

    class Meta:
        ordering = ['CreatedAt']

    def __str__(self):
        return f'Bình luận của {self.User.username} về {self.Novel.Name}'