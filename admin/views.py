from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.paginator import Paginator
from students.models import StudentProfile
from notifications.models import Notification
from django.contrib import messages
import json


def is_admin(user):
    """بررسی اینکه کاربر ادمین است یا نه"""
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def verification_management(request):
    """مدیریت احراز هویت دانشجویان"""
    # فیلترها
    status_filter = request.GET.get('status')
    university_filter = request.GET.get('university')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # دریافت درخواست‌های احراز هویت
    verification_requests = StudentProfile.objects.filter(
        verification_status__in=['pending', 'approved', 'rejected']
    ).select_related('user')
    
    # اعمال فیلترها
    if status_filter:
        verification_requests = verification_requests.filter(verification_status=status_filter)
    
    if university_filter:
        verification_requests = verification_requests.filter(university__icontains=university_filter)
    
    if date_from:
        verification_requests = verification_requests.filter(updated_at__date__gte=date_from)
    
    if date_to:
        verification_requests = verification_requests.filter(updated_at__date__lte=date_to)
    
    # مرتب‌سازی
    verification_requests = verification_requests.order_by('-updated_at')
    
    # صفحه‌بندی
    paginator = Paginator(verification_requests, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # آمار
    pending_count = StudentProfile.objects.filter(verification_status='pending').count()
    approved_count = StudentProfile.objects.filter(verification_status='approved').count()
    rejected_count = StudentProfile.objects.filter(verification_status='rejected').count()
    
    return render(request, 'admin/verification_management.html', {
        'verification_requests': page_obj,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count
    })


@login_required
@user_passes_test(is_admin)
def approve_verification(request, profile_id):
    """تایید احراز هویت"""
    if request.method == 'POST':
        profile = get_object_or_404(StudentProfile, id=profile_id)
        profile.verification_status = 'approved'
        profile.is_student_verified = True
        profile.save()
        
        # ارسال نوتیفیکیشن به دانشجو
        Notification.objects.create(
            user=profile.user,
            title='احراز هویت تایید شد',
            message='تبریک! احراز هویت دانشجویی شما تایید شد.',
            notification_type='verification'
        )
        
        return JsonResponse({'success': True, 'message': 'احراز هویت تایید شد'})
    
    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


@login_required
@user_passes_test(is_admin)
def reject_verification(request, profile_id):
    """رد احراز هویت"""
    if request.method == 'POST':
        data = json.loads(request.body)
        reason = data.get('reason', 'دلیل مشخص نشده')
        
        profile = get_object_or_404(StudentProfile, id=profile_id)
        profile.verification_status = 'rejected'
        profile.verification_notes = reason
        profile.save()
        
        # ارسال نوتیفیکیشن به دانشجو
        Notification.objects.create(
            user=profile.user,
            title='احراز هویت رد شد',
            message=f'متاسفانه احراز هویت شما رد شد. دلیل: {reason}',
            notification_type='verification'
        )
        
        return JsonResponse({'success': True, 'message': 'احراز هویت رد شد'})
    
    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})


@login_required
@user_passes_test(is_admin)
def verification_details(request, profile_id):
    """جزئیات درخواست احراز هویت"""
    profile = get_object_or_404(StudentProfile, id=profile_id)
    
    return render(request, 'admin/verification_details.html', {
        'profile': profile
    })


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """داشبورد ادمین"""
    # آمار کلی
    total_students = StudentProfile.objects.count()
    total_companies = StudentProfile.objects.filter(user__user_type='company').count()
    pending_verifications = StudentProfile.objects.filter(verification_status='pending').count()
    total_matches = 0  # اینجا می‌توانید آمار مچینگ را اضافه کنید
    
    # آمار اخیر
    recent_verifications = StudentProfile.objects.filter(
        verification_status__in=['pending', 'approved', 'rejected']
    ).order_by('-updated_at')[:5]
    
    return render(request, 'admin/dashboard.html', {
        'total_students': total_students,
        'total_companies': total_companies,
        'pending_verifications': pending_verifications,
        'total_matches': total_matches,
        'recent_verifications': recent_verifications
    })
