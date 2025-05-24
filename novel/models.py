from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.exceptions import ValidationError


class CustomUser(AbstractUser):
    sdt = models.CharField(max_length=15, blank=True, null=True, verbose_name="Số điện thoại")  
    is_admin = models.BooleanField(default=False, verbose_name="Là Admin")  

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name or self.username


class Novel(models.Model):
    NovelId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255, unique=True)
    ViewCount = models.IntegerField(default=0)
    Description = models.TextField()
    Author = models.CharField(max_length=255)
    State = models.CharField(max_length=50)
    ChapCount = models.IntegerField(default=0)
    ImgUrl = models.URLField(max_length=500, blank=True, null=True)
    dateUpdate = models.DateTimeField(auto_now=True)
    TotalComments = models.IntegerField(default=0)

    def __str__(self):
        return self.Name

    def get_absolute_url(self):
        return reverse("novel_detail", args=[str(self.NovelId)])

    def update_view_count(self):
        self.ViewCount += 1
        self.save()
    def get_followers_count(self):
        return self.reading_progress.count()


class Chapter(models.Model):
    ChapId = models.AutoField(primary_key=True)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters')
    Name = models.CharField(max_length=255)
    Number = models.IntegerField()
    Content = models.TextField()
    dateUpdate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.Novel.Name} - Chương {self.Number}: {self.Name}'

    def get_absolute_url(self):
        return reverse("chapter_detail", args=[str(self.ChapId)])


class Category(models.Model):
    CategoryId = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=255)

    def __str__(self):
        return self.Name


class CategoryNovel(models.Model):
    CNId = models.AutoField(primary_key=True)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.Novel.Name} - {self.Category.Name}'


class UserNovel(models.Model):
    UNId = models.AutoField(primary_key=True)
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.User.username} yêu thích {self.Novel.Name}'


class Comment(models.Model):
    _id = models.AutoField(primary_key=True)
    CommentId = models.IntegerField()
    Content = models.TextField()
    User = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    Novel = models.ForeignKey(Novel, on_delete=models.CASCADE,related_name='comments')
    CreatedAt = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    class Meta:
        ordering = ['CreatedAt']

    def __str__(self):
        return f'Bình luận của {self.User.username} về {self.Novel.Name}'

    def is_reply(self):
        return self.parent_comment is not None


class ReadingProgress(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='reading_progress')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='reading_progress')
    current_chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='current_readers')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'novel') 

    def clean(self):
        if self.current_chapter.Novel != self.novel:
            raise ValidationError("Chương được chọn không thuộc truyện đã chọn.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} đang đọc {self.novel.Name} - Chương {self.current_chapter.Number}'

    def get_absolute_url(self):
        return reverse("reading_progress_detail", args=[str(self.id)])
