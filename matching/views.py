from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Match, MatchCriteria, MatchHistory
from .matching_algorithm import calculate_match_score


@login_required
def matching_algorithm(request):
    """الگوریتم مچینگ"""
    if request.user.user_type == 'company':
        # برای شرکت‌ها، دانشجویان مناسب را نمایش می‌دهیم
        from students.models import StudentRequest
        from companies.models import JobRequest
        from django.core.paginator import Paginator
        
        # دریافت درخواست‌های شغلی شرکت
        company_job_requests = JobRequest.objects.filter(company=request.user, is_active=True)
        
        if not company_job_requests.exists():
            return render(request, 'matching/no_job_requests.html')
        
        # فیلترهای جستجو
        field_filter = request.GET.get('field')
        job_type_filter = request.GET.get('job_type')
        city_filter = request.GET.get('city')
        score_filter = request.GET.get('score')
        
        # دریافت درخواست‌های دانشجویان با فیلتر
        student_requests = StudentRequest.objects.filter(is_active=True)
        
        if field_filter:
            student_requests = student_requests.filter(field_of_study__icontains=field_filter)
        if job_type_filter:
            student_requests = student_requests.filter(job_type=job_type_filter)
        if city_filter:
            student_requests = student_requests.filter(city__icontains=city_filter)
        
        # محاسبه امتیاز مچینگ برای هر دانشجو
        matches = []
        for student_request in student_requests:
            for job_request in company_job_requests:
                match_score = calculate_match_score(student_request, job_request)
                min_score = int(score_filter) if score_filter else 50
                
                if match_score >= min_score:
                    matches.append({
                        'student': student_request.user,
                        'student_request': student_request,
                        'job_request': job_request,
                        'match_score': match_score
                    })
        
        # مرتب‌سازی بر اساس امتیاز
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # صفحه‌بندی
        paginator = Paginator(matches, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'companies/matching.html', {
            'candidates': page_obj,
            'total_matches': len(matches)
        })
    
    else:
        # برای دانشجویان، شرکت‌های مناسب را نمایش می‌دهیم
        from companies.models import JobRequest
        job_requests = JobRequest.objects.filter(is_active=True)
        
        # محاسبه امتیاز مچینگ برای هر شرکت
        matches = []
        for job_request in job_requests:
            score = calculate_match_score(request.user.student_requests.first(), job_request.company)
            if score > 0.5:
                matches.append({
                    'job_request': job_request,
                    'score': score
                })
        
        # مرتب‌سازی بر اساس امتیاز
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return render(request, 'matching/student_matching.html', {'matches': matches})


@login_required
def matches(request):
    """لیست مچینگ‌ها"""
    if request.user.user_type == 'company':
        matches = Match.objects.filter(company=request.user)
    else:
        matches = Match.objects.filter(student=request.user)
    
    return render(request, 'matching/matches.html', {'matches': matches})


@login_required
def match_detail(request, match_id):
    """جزئیات مچینگ"""
    match = get_object_or_404(Match, id=match_id)
    
    # بررسی دسترسی کاربر
    if request.user not in [match.student, match.company]:
        messages.error(request, 'شما دسترسی به این مچینگ ندارید!')
        return redirect('matching:matches')
    
    return render(request, 'matching/match_detail.html', {'match': match})


@login_required
def accept_match(request, match_id):
    """پذیرش مچینگ"""
    match = get_object_or_404(Match, id=match_id)
    
    if request.user == match.company:
        match.status = 'accepted'
        match.save()
        
        # ایجاد تاریخچه
        MatchHistory.objects.create(
            match=match,
            action='accepted',
            user=request.user,
            message='شرکت مچینگ را پذیرفت'
        )
        
        # ارسال نوتیفیکیشن به دانشجو
        from notifications.models import Notification
        Notification.objects.create(
            user=match.student,
            title='مچینگ پذیرفته شد',
            message=f'شرکت {match.company.company_profile.company_name} مچینگ شما را پذیرفت',
            notification_type='match'
        )
        
        messages.success(request, 'مچینگ با موفقیت پذیرفته شد!')
    
    elif request.user == match.student:
        match.status = 'accepted'
        match.save()
        
        # ایجاد تاریخچه
        MatchHistory.objects.create(
            match=match,
            action='accepted',
            user=request.user,
            message='دانشجو مچینگ را پذیرفت'
        )
        
        # ارسال نوتیفیکیشن به شرکت
        from notifications.models import Notification
        Notification.objects.create(
            user=match.company,
            title='مچینگ پذیرفته شد',
            message=f'دانشجو {match.student.get_full_name()} مچینگ شما را پذیرفت',
            notification_type='match'
        )
        
        messages.success(request, 'مچینگ با موفقیت پذیرفته شد!')
    
    return redirect('matching:match_detail', match_id=match_id)


@login_required
def reject_match(request, match_id):
    """رد مچینگ"""
    match = get_object_or_404(Match, id=match_id)
    
    if request.user == match.company:
        match.status = 'rejected'
        match.save()
        
        # ایجاد تاریخچه
        MatchHistory.objects.create(
            match=match,
            action='rejected',
            user=request.user,
            message='شرکت مچینگ را رد کرد'
        )
        
        messages.success(request, 'مچینگ رد شد!')
    
    elif request.user == match.student:
        match.status = 'rejected'
        match.save()
        
        # ایجاد تاریخچه
        MatchHistory.objects.create(
            match=match,
            action='rejected',
            user=request.user,
            message='دانشجو مچینگ را رد کرد'
        )
        
        messages.success(request, 'مچینگ رد شد!')
    
    return redirect('matching:matches')


@login_required
def select_candidate(request, candidate_id):
    """انتخاب کاندیدا توسط شرکت"""
    if request.user.user_type != 'company':
        return JsonResponse({'success': False, 'message': 'دسترسی غیرمجاز'})
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        candidate = User.objects.get(id=candidate_id, user_type='student')
        
        # ایجاد مچینگ جدید
        match = Match.objects.create(
            student=candidate,
            company=request.user,
            match_score=0,  # امتیاز بعداً محاسبه می‌شود
            status='pending'
        )
        
        # ارسال نوتیفیکیشن به دانشجو
        from notifications.models import Notification
        Notification.objects.create(
            user=candidate,
            title='درخواست شغلی جدید',
            message=f'شرکت {request.user.company_profile.company_name} به شما درخواست شغلی داده است.',
            notification_type='match'
        )
        
        return JsonResponse({'success': True, 'message': 'کاندیدا با موفقیت انتخاب شد'})
        
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'کاندیدا یافت نشد'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
