from django import forms
from .models import CompanyProfile, JobRequest


class CompanyProfileForm(forms.ModelForm):
    """فرم پروفایل شرکت"""
    
    class Meta:
        model = CompanyProfile
        fields = ("company_name", "company_type", "industry", "company_size", "website", "address", "city", "province", "description", "verification_document")
        labels = {
            "company_name": "نام شرکت",
            "company_type": "نوع شرکت",
            "industry": "صنعت",
            "company_size": "اندازه شرکت",
            "website": "وب‌سایت",
            "address": "آدرس",
            "city": "شهر",
            "province": "استان",
            "description": "توضیحات شرکت",
            "verification_document": "مدرک تایید شرکت",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 4, "class": "form-control"})


class JobRequestForm(forms.ModelForm):
    """فرم درخواست شغلی"""
    
    class Meta:
        model = JobRequest
        fields = ("title", "field_of_study", "job_type", "work_type", "city", "province", "required_skills", "min_age", "max_age", "min_salary", "max_salary", "number_of_positions", "description", "requirements", "benefits")
        labels = {
            "title": "عنوان شغل",
            "field_of_study": "رشته تحصیلی مورد نیاز",
            "job_type": "نوع شغل",
            "work_type": "نوع کار",
            "city": "شهر",
            "province": "استان",
            "required_skills": "مهارت‌های مورد نیاز",
            "min_age": "حداقل سن",
            "max_age": "حداکثر سن",
            "min_salary": "حداقل حقوق",
            "max_salary": "حداکثر حقوق",
            "number_of_positions": "تعداد موقعیت‌های شغلی",
            "description": "توضیحات شغل",
            "requirements": "الزامات",
            "benefits": "مزایا",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["required_skills"].widget = forms.Textarea(attrs={"rows": 3, "class": "form-control"})
        self.fields["description"].widget = forms.Textarea(attrs={"rows": 4, "class": "form-control"})
        self.fields["requirements"].widget = forms.Textarea(attrs={"rows": 3, "class": "form-control"})
        self.fields["benefits"].widget = forms.Textarea(attrs={"rows": 3, "class": "form-control"})
