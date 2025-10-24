from django import forms
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


class MessageForm(forms.ModelForm):
    """فرم ارسال پیام"""
    
    class Meta:
        model = Message
        fields = ("receiver", "subject", "message", "message_type", "attachment")
        labels = {
            "receiver": "گیرنده",
            "subject": "موضوع",
            "message": "پیام",
            "message_type": "نوع پیام",
            "attachment": "ضمیمه",
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فیلتر کردن کاربران برای انتخاب گیرنده
        self.fields["receiver"].queryset = User.objects.exclude(id=self.initial.get("sender_id", 0))
        
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
        
        self.fields["message"].widget = forms.Textarea(attrs={"rows": 4, "class": "form-control"})
