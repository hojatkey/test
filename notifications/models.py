from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Notification(models.Model):
    """نوتیفیکیشن"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('match', 'مچینگ جدید'),
        ('message', 'پیام جدید'),
        ('verification', 'تایید احراز هویت'),
        ('test_result', 'نتیجه آزمون'),
        ('job_offer', 'پیشنهاد شغل'),
        ('system', 'سیستم'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='کاربر'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان'
    )
    
    message = models.TextField(
        verbose_name='پیام'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        verbose_name='نوع نوتیفیکیشن'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='خوانده شده'
    )
    
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='شناسه شیء مرتبط'
    )
    
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='نوع شیء مرتبط'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        verbose_name = 'نوتیفیکیشن'
        verbose_name_plural = 'نوتیفیکیشن‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"


class Message(models.Model):
    """پیام بین کاربران"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'متن'),
        ('file', 'فایل'),
        ('image', 'تصویر'),
    ]
    
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='فرستنده'
    )
    
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='گیرنده'
    )
    
    subject = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='موضوع'
    )
    
    message = models.TextField(
        verbose_name='پیام'
    )
    
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
        verbose_name='نوع پیام'
    )
    
    attachment = models.FileField(
        upload_to='message_attachments/',
        blank=True,
        null=True,
        verbose_name='ضمیمه'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='خوانده شده'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        verbose_name = 'پیام'
        verbose_name_plural = 'پیام‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()} -> {self.receiver.get_full_name()}"
