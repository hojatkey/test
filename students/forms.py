from django import forms
from .models import StudentProfile, StudentRequest, StudentFile


class StudentProfileForm(forms.ModelForm):
    """فرم پروفایل دانشجو"""
    
    class Meta:
        model = StudentProfile
        fields = ("student_id", "university", "field_of_study", "degree_level", "graduation_year", "gpa", "verification_document")
        labels = {
            "student_id": "شماره دانشجویی",
            "university": "دانشگاه",
            "field_of_study": "رشته تحصیلی",
            "degree_level": "مقطع تحصیلی",
            "graduation_year": "سال فارغ‌التحصیلی",
            "gpa": "معدل",
            "verification_document": "مدرک احراز هویت",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class StudentRequestForm(forms.ModelForm):
    """فرم درخواست دانشجو"""
    
    class Meta:
        model = StudentRequest
        fields = ("city", "province", "job_type", "work_type", "skills", "field_of_study", "is_available_for_employment", "expected_salary", "description")
        labels = {
            "city": "شهر",
            "province": "استان",
            "job_type": "نوع شغل",
            "work_type": "نوع کار",
            "skills": "مهارت‌ها",
            "field_of_study": "رشته تحصیلی",
            "is_available_for_employment": "قابل استخدام",
            "expected_salary": "حقوق مورد انتظار",
            "description": "توضیحات",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["skills"].widget = forms.Textarea(attrs={"rows": 3, "class": "form-control"})
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 4, "class": "form-control"})


class StudentFileForm(forms.ModelForm):
    """فرم آپلود فایل دانشجو"""
    
    class Meta:
        model = StudentFile
        fields = ("file", "file_type", "title", "description")
        labels = {
            "file": "فایل",
            "file_type": "نوع فایل",
            "title": "عنوان",
            "description": "توضیحات",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 3, "class": "form-control"})


class StudentVerificationForm(forms.ModelForm):
    """فرم احراز هویت دانشجویی"""
    
    class Meta:
        model = StudentProfile
        fields = ('student_id_document', 'national_id_document', 'university_email', 'additional_info')
        labels = {
            'student_id_document': 'کارت دانشجویی یا گواهی اشتغال به تحصیل',
            'national_id_document': 'کارت ملی یا شناسنامه',
            'university_email': 'ایمیل دانشگاهی',
            'additional_info': 'اطلاعات اضافی',
        }
        widgets = {
            'additional_info': forms.Textarea(attrs={'rows': 4, 'placeholder': 'هر اطلاعات اضافی که فکر می‌کنید مفید است...', 'class': 'form-control'}),
            'university_email': forms.EmailInput(attrs={'placeholder': 'example@university.ac.ir', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.__class__ not in [forms.Textarea, forms.EmailInput]:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_student_id_document(self):
        document = self.cleaned_data.get('student_id_document')
        if document:
            if document.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('حجم فایل نباید بیشتر از 5 مگابایت باشد.')
            if not document.content_type in ['application/pdf', 'image/jpeg', 'image/png']:
                raise forms.ValidationError('فرمت فایل باید PDF، JPG یا PNG باشد.')
        return document
    
    def clean_national_id_document(self):
        document = self.cleaned_data.get('national_id_document')
        if document:
            if document.size > 5 * 1024 * 1024:  # 5MB
                raise forms.ValidationError('حجم فایل نباید بیشتر از 5 مگابایت باشد.')
            if not document.content_type in ['application/pdf', 'image/jpeg', 'image/png']:
                raise forms.ValidationError('فرمت فایل باید PDF، JPG یا PNG باشد.')
        return document
