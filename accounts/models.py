from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """مدل کاربر سفارشی"""
    
    USER_TYPE_CHOICES = [
        ('student', 'دانشجو'),
        ('company', 'شرکت'),
        ('admin', 'مدیر'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        verbose_name='نوع کاربر'
    )
    
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='شماره تلفن'
    )
    
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name='تصویر پروفایل'
    )
    
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='بیوگرافی'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تایید شده'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ به‌روزرسانی'
    )
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    def get_user_type_display(self):
        return dict(self.USER_TYPE_CHOICES)[self.user_type]
