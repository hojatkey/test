from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Notification, Message
from .forms import MessageForm


@login_required
def notifications(request):
    """لیست نوتیفیکیشن‌ها"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # علامت‌گذاری همه نوتیفیکیشن‌ها به عنوان خوانده شده
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'notifications/notifications.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    """علامت‌گذاری نوتیفیکیشن به عنوان خوانده شده"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({'status': 'success'})
    
    messages.success(request, 'نوتیفیکیشن خوانده شد!')
    return redirect('notifications:notifications')


@login_required
def messages_list(request):
    """لیست پیام‌ها"""
    received_messages = Message.objects.filter(receiver=request.user).order_by('-created_at')
    sent_messages = Message.objects.filter(sender=request.user).order_by('-created_at')
    
    return render(request, 'notifications/messages.html', {
        'received_messages': received_messages,
        'sent_messages': sent_messages
    })


@login_required
def send_message(request):
    """ارسال پیام"""
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # ارسال نوتیفیکیشن به گیرنده
            Notification.objects.create(
                user=message.receiver,
                title='پیام جدید',
                message=f'شما پیام جدیدی از {message.sender.get_full_name()} دریافت کردید',
                notification_type='message'
            )
            
            messages.success(request, 'پیام با موفقیت ارسال شد!')
            return redirect('notifications:messages')
    else:
        form = MessageForm()
    
    return render(request, 'notifications/send_message.html', {'form': form})


@login_required
def message_detail(request, message_id):
    """جزئیات پیام"""
    message = get_object_or_404(Message, id=message_id)
    
    # بررسی دسترسی کاربر
    if request.user not in [message.sender, message.receiver]:
        messages.error(request, 'شما دسترسی به این پیام ندارید!')
        return redirect('notifications:messages')
    
    # علامت‌گذاری پیام به عنوان خوانده شده اگر گیرنده آن هستیم
    if request.user == message.receiver and not message.is_read:
        message.is_read = True
        message.save()
    
    return render(request, 'notifications/message_detail.html', {'message': message})
