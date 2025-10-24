from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Match(models.Model):
    """مچینگ بین دانشجو و شرکت"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'رد شده'),
        ('expired', 'منقضی شده'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_student',
        verbose_name='دانشجو'
    )
    
    company = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='matches_as_company',
        verbose_name='شرکت'
    )
    
    job_request = models.ForeignKey(
        'companies.JobRequest',
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name='درخواست شغلی'
    )
    
    student_request = models.ForeignKey(
        'students.StudentRequest',
        on_delete=models.CASCADE,
        related_name='matches',
        verbose_name='درخواست دانشجو'
    )
    
    match_score = models.FloatField(
        verbose_name='امتیاز مچینگ'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    company_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='پیام شرکت'
    )
    
    student_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='پیام دانشجو'
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
        verbose_name = 'مچینگ'
        verbose_name_plural = 'مچینگ‌ها'
        unique_together = ['student', 'job_request']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.company.company_profile.company_name}"


class MatchCriteria(models.Model):
    """معیارهای مچینگ"""
    
    name = models.CharField(
        max_length=100,
        verbose_name='نام معیار'
    )
    
    weight = models.FloatField(
        default=1.0,
        verbose_name='وزن'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        verbose_name = 'معیار مچینگ'
        verbose_name_plural = 'معیارهای مچینگ'
    
    def __str__(self):
        return self.name


class MatchHistory(models.Model):
    """تاریخچه مچینگ"""
    
    ACTION_CHOICES = [
        ('created', 'ایجاد شده'),
        ('viewed', 'مشاهده شده'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'رد شده'),
        ('contacted', 'تماس گرفته شده'),
    ]
    
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name='مچینگ'
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='عمل'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='کاربر'
    )
    
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name='پیام'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    
    class Meta:
        verbose_name = 'تاریخچه مچینگ'
        verbose_name_plural = 'تاریخچه مچینگ‌ها'
    
    def __str__(self):
        return f"{self.match} - {self.get_action_display()}"
