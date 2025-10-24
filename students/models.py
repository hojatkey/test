from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class StudentProfile(models.Model):
    """پروفایل دانشجو"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='کاربر'
    )
    
    student_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره دانشجویی'
    )
    
    university = models.CharField(
        max_length=200,
        verbose_name='دانشگاه'
    )
    
    field_of_study = models.CharField(
        max_length=100,
        verbose_name='رشته تحصیلی'
    )
    
    degree_level = models.CharField(
        max_length=50,
        choices=[
            ('bachelor', 'کارشناسی'),
            ('master', 'کارشناسی ارشد'),
            ('phd', 'دکتری'),
        ],
        verbose_name='مقطع تحصیلی'
    )
    
    graduation_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='سال فارغ‌التحصیلی'
    )
    
    gpa = models.FloatField(
        null=True,
        blank=True,
        verbose_name='معدل'
    )
    
    is_student_verified = models.BooleanField(
        default=False,
        verbose_name='احراز هویت دانشجویی'
    )
    
    verification_document = models.FileField(
        upload_to='verification_documents/',
        blank=True,
        null=True,
        verbose_name='مدرک احراز هویت'
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
        verbose_name = 'پروفایل دانشجو'
        verbose_name_plural = 'پروفایل‌های دانشجو'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.university}"


class StudentRequest(models.Model):
    """درخواست شغلی دانشجو"""
    
    JOB_TYPE_CHOICES = [
        ('internship', 'کارآموزی'),
        ('part_time', 'نیمه‌وقت'),
        ('full_time', 'تمام‌وقت'),
        ('project', 'پروژه‌ای'),
        ('freelance', 'فریلنسری'),
    ]
    
    WORK_TYPE_CHOICES = [
        ('remote', 'دورکاری'),
        ('office', 'حضوری'),
        ('hybrid', 'ترکیبی'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='student_requests',
        verbose_name='دانشجو'
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
    
    skills = models.TextField(
        verbose_name='مهارت‌ها'
    )
    
    field_of_study = models.CharField(
        max_length=100,
        verbose_name='رشته تحصیلی'
    )
    
    is_available_for_employment = models.BooleanField(
        default=True,
        verbose_name='قابل استخدام'
    )
    
    expected_salary = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='حقوق مورد انتظار'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
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
        verbose_name = 'درخواست دانشجو'
        verbose_name_plural = 'درخواست‌های دانشجو'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_job_type_display()}"


class PersonalityTest(models.Model):
    """آزمون شخصیتی"""
    
    TEST_TYPE_CHOICES = [
        ('big_five', 'پنج عامل بزرگ شخصیت'),
        ('mbti', 'MBTI'),
        ('disc', 'DISC'),
        ('custom', 'سفارشی'),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name='نام آزمون'
    )
    
    test_type = models.CharField(
        max_length=20,
        choices=TEST_TYPE_CHOICES,
        verbose_name='نوع آزمون'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
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
        verbose_name = 'آزمون شخصیتی'
        verbose_name_plural = 'آزمون‌های شخصیتی'
    
    def __str__(self):
        return self.name


class StudentTestResult(models.Model):
    """نتیجه آزمون دانشجو"""
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='دانشجو'
    )
    
    test = models.ForeignKey(
        PersonalityTest,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='آزمون'
    )
    
    score = models.FloatField(
        verbose_name='نمره'
    )
    
    result_data = models.JSONField(
        verbose_name='داده‌های نتیجه'
    )
    
    completed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ تکمیل'
    )
    
    class Meta:
        verbose_name = 'نتیجه آزمون'
        verbose_name_plural = 'نتایج آزمون‌ها'
        unique_together = ['student', 'test']
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.test.name}"


class StudentFile(models.Model):
    """فایل‌های دانشجو"""
    
    FILE_TYPE_CHOICES = [
        ('resume', 'رزومه'),
        ('portfolio', 'نمونه کار'),
        ('certificate', 'گواهینامه'),
        ('project', 'پروژه'),
        ('other', 'سایر'),
    ]
    
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='دانشجو'
    )
    
    file = models.FileField(
        upload_to='student_files/',
        verbose_name='فایل'
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        verbose_name='نوع فایل'
    )
    
    title = models.CharField(
        max_length=200,
        verbose_name='عنوان'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='توضیحات'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ آپلود'
    )
    
    class Meta:
        verbose_name = 'فایل دانشجو'
        verbose_name_plural = 'فایل‌های دانشجو'
    
    def __str__(self):
        return f"{self.student.get_full_name()} - {self.title}"
