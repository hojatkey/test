from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CompanyProfile(models.Model):
    """پروفایل شرکت"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile',
        verbose_name='کاربر'
    )
    
    company_name = models.CharField(
        max_length=200,
        verbose_name='نام شرکت'
    )
    
    company_type = models.CharField(
        max_length=100,
        choices=[
            ('startup', 'استارتاپ'),
            ('small', 'شرکت کوچک'),
            ('medium', 'شرکت متوسط'),
            ('large', 'شرکت بزرگ'),
            ('multinational', 'چندملیتی'),
        ],
        verbose_name='نوع شرکت'
    )
    
    industry = models.CharField(
        max_length=100,
        verbose_name='صنعت'
    )
    
    company_size = models.CharField(
        max_length=50,
        choices=[
            ('1-10', '1-10 نفر'),
            ('11-50', '11-50 نفر'),
            ('51-200', '51-200 نفر'),
            ('201-500', '201-500 نفر'),
            ('500+', 'بیش از 500 نفر'),
        ],
        verbose_name='اندازه شرکت'
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name='وب‌سایت'
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name='آدرس'
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شهر'
    )
    
    province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='استان'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات شرکت'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تایید شده'
    )
    
    verification_document = models.FileField(
        upload_to='company_verification/',
        blank=True,
        null=True,
        verbose_name='مدرک تایید شرکت'
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
        verbose_name = 'پروفایل شرکت'
        verbose_name_plural = 'پروفایل‌های شرکت'
    
    def __str__(self):
        return self.company_name


class JobRequest(models.Model):
    """درخواست شغلی شرکت"""
    
    JOB_TYPE_CHOICES = [
        ('internship', 'کارآموزی'),
        ('part_time', 'نیمه‌وقت'),
        ('full_time', 'تمام‌وقت'),
        ('project', 'پروژه‌ای'),
    ]
    
    WORK_TYPE_CHOICES = [
        ('remote', 'دورکاری'),
        ('office', 'حضوری'),
        ('hybrid', 'ترکیبی'),
    ]
    
    company = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='job_requests',
        verbose_name='شرکت'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان شغل'
    )
    
    field_of_study = models.CharField(
        max_length=100,
        verbose_name='رشته تحصیلی مورد نیاز'
    )
    
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        verbose_name='نوع شغل'
    )
    
    work_type = models.CharField(
        max_length=20,
        choices=WORK_TYPE_CHOICES,
        verbose_name='نوع کار'
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شهر'
    )
    
    province = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='استان'
    )
    
    required_skills = models.TextField(
        verbose_name='مهارت‌های مورد نیاز'
    )
    
    min_age = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='حداقل سن'
    )
    
    max_age = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='حداکثر سن'
    )
    
    min_salary = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='حداقل حقوق'
    )
    
    max_salary = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='حداکثر حقوق'
    )
    
    number_of_positions = models.IntegerField(
        default=1,
        verbose_name='تعداد موقعیت‌های شغلی'
    )
    
    description = models.TextField(
        verbose_name='توضیحات شغل'
    )
    
    requirements = models.TextField(
        blank=True,
        null=True,
        verbose_name='الزامات'
    )
    
    benefits = models.TextField(
        blank=True,
        null=True,
        verbose_name='مزایا'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
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
        verbose_name = 'درخواست شغلی'
        verbose_name_plural = 'درخواست‌های شغلی'
    
    def __str__(self):
        return f"{self.company.company_profile.company_name} - {self.title}"
