from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import CompanyProfile, JobRequest
from .forms import CompanyProfileForm, JobRequestForm


@login_required
def company_profile(request):
    """پروفایل شرکت"""
    try:
        profile = request.user.company_profile
    except CompanyProfile.DoesNotExist:
        profile = None
    
    return render(request, 'companies/profile.html', {'profile': profile})


@login_required
def job_requests(request):
    """درخواست‌های شغلی شرکت"""
    requests = JobRequest.objects.filter(company=request.user)
    return render(request, 'companies/requests.html', {'requests': requests})


@login_required
def create_job_request(request):
    """ایجاد درخواست شغلی جدید"""
    if request.method == 'POST':
        form = JobRequestForm(request.POST)
        if form.is_valid():
            job_request = form.save(commit=False)
            job_request.company = request.user
            job_request.save()
            messages.success(request, 'درخواست شغلی با موفقیت ایجاد شد!')
            return redirect('companies:requests')
    else:
        form = JobRequestForm()
    
    return render(request, 'companies/create_job_request.html', {'form': form})


@login_required
def edit_job_request(request, request_id):
    """ویرایش درخواست شغلی"""
    job_request = get_object_or_404(JobRequest, id=request_id, company=request.user)
    
    if request.method == 'POST':
        form = JobRequestForm(request.POST, instance=job_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست شغلی با موفقیت به‌روزرسانی شد!')
            return redirect('companies:requests')
    else:
        form = JobRequestForm(instance=job_request)
    
    return render(request, 'companies/edit_job_request.html', {'form': form, 'request': job_request})


@login_required
def matching(request):
    """صفحه مچینگ شرکت"""
    # در اینجا الگوریتم مچینگ پیاده‌سازی می‌شود
    # برای سادگی، تمام درخواست‌های فعال دانشجویان را نمایش می‌دهیم
    from students.models import StudentRequest
    student_requests = StudentRequest.objects.filter(is_active=True)
    
    return render(request, 'companies/matching.html', {'student_requests': student_requests})


@login_required
def candidates(request):
    """لیست کاندیداها"""
    # در اینجا کاندیداهای مچ شده نمایش داده می‌شوند
    from matching.models import Match
    matches = Match.objects.filter(company=request.user, status='pending')
    
    return render(request, 'companies/candidates.html', {'matches': matches})


@login_required
def candidate_detail(request, student_id):
    """جزئیات کاندیدا"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    student = get_object_or_404(User, id=student_id, user_type='student')
    
    try:
        student_profile = student.student_profile
    except:
        student_profile = None
    
    student_requests = student.student_requests.filter(is_active=True)
    test_results = student.test_results.all()
    
    return render(request, 'companies/candidate_detail.html', {
        'student': student,
        'student_profile': student_profile,
        'student_requests': student_requests,
        'test_results': test_results,
    })
