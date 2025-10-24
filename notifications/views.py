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
    unread_notifications = notifications.filter(is_read=False)
    unread_count = unread_notifications.count()
    
    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count
    })


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


# Real-time notifications
@login_required
def notification_stream(request):
    """استریم نوتیفیکیشن‌های real-time"""
    from django.http import StreamingHttpResponse
    import json
    import time
    
    def event_stream():
        while True:
            # دریافت نوتیفیکیشن‌های جدید
            new_notifications = Notification.objects.filter(
                user=request.user,
                is_read=False
            ).order_by('-created_at')[:5]
            
            for notification in new_notifications:
                data = {
                    'id': notification.id,
                    'title': notification.title,
                    'message': notification.message,
                    'type': notification.notification_type,
                    'created_at': notification.created_at.isoformat()
                }
                yield f"data: {json.dumps(data)}\n\n"
            
            time.sleep(5)  # بررسی هر 5 ثانیه
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    return response


# API Views
@login_required
def mark_notification_read_api(request, notification_id):
    """API برای علامت‌گذاری نوتیفیکیشن به عنوان خوانده شده"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    return JsonResponse({'success': True})


@login_required
def mark_all_read_api(request):
    """API برای علامت‌گذاری همه نوتیفیکیشن‌ها به عنوان خوانده شده"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return JsonResponse({'success': True})


@login_required
def delete_notification_api(request, notification_id):
    """API برای حذف نوتیفیکیشن"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    
    return JsonResponse({'success': True})


@login_required
def unread_count_api(request):
    """API برای تعداد نوتیفیکیشن‌های خوانده نشده"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
