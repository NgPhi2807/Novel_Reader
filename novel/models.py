from django.db import models

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
    

class Chapter(models.Model):
    ChapId = models.AutoField(primary_key=True)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    Name = models.CharField(max_length=255)
    Number = models.IntegerField()
    Content = models.TextField()
    dateUpdate = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Chương {self.Number}: {self.Name}"
   
    
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
    CommentId = models.AutoField(primary_key=True)
    Content = models.TextField()
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
