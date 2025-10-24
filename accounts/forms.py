from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """فرم ثبت نام کاربر"""
    
    email = forms.EmailField(required=True, label="ایمیل")
    first_name = forms.CharField(max_length=30, required=True, label="نام")
    last_name = forms.CharField(max_length=30, required=True, label="نام خانوادگی")
    phone_number = forms.CharField(max_length=15, required=False, label="شماره تلفن")
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        required=True,
        label="نوع کاربر"
    )
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone_number", "user_type", "password1", "password2")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "نام کاربری"
        self.fields["password1"].label = "رمز عبور"
        self.fields["password2"].label = "تکرار رمز عبور"
        
        # اضافه کردن کلاس‌های CSS
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class UserLoginForm(forms.Form):
    """فرم ورود کاربر"""
    
    username = forms.CharField(max_length=150, label="نام کاربری")
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["class"] = "form-control"
        self.fields["password"].widget.attrs["class"] = "form-control"


class UserProfileForm(forms.ModelForm):
    """فرم ویرایش پروفایل کاربر"""
    
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone_number", "profile_image", "bio")
        labels = {
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "email": "ایمیل",
            "phone_number": "شماره تلفن",
            "profile_image": "تصویر پروفایل",
            "bio": "بیوگرافی",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["bio"].widget = forms.Textarea(attrs={"rows": 4, "class": "form-control"})
