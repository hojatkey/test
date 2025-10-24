from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import StudentProfile, StudentRequest, PersonalityTest, StudentTestResult, StudentFile
from .forms import StudentProfileForm, StudentRequestForm, StudentFileForm


@login_required
def student_profile(request):
    """پروفایل دانشجو"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        profile = None
    
    return render(request, 'students/profile.html', {'profile': profile})


@login_required
def student_requests(request):
    """درخواست‌های دانشجو"""
    requests = StudentRequest.objects.filter(user=request.user)
    return render(request, 'students/requests.html', {'requests': requests})


@login_required
def create_request(request):
    """ایجاد درخواست جدید"""
    if request.method == 'POST':
        form = StudentRequestForm(request.POST)
        if form.is_valid():
            student_request = form.save(commit=False)
            student_request.user = request.user
            student_request.save()
            messages.success(request, 'درخواست با موفقیت ایجاد شد!')
            return redirect('students:requests')
    else:
        form = StudentRequestForm()
    
    return render(request, 'students/create_request.html', {'form': form})


@login_required
def edit_request(request, request_id):
    """ویرایش درخواست"""
    student_request = get_object_or_404(StudentRequest, id=request_id, user=request.user)
    
    if request.method == 'POST':
        form = StudentRequestForm(request.POST, instance=student_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'درخواست با موفقیت به‌روزرسانی شد!')
            return redirect('students:requests')
    else:
        form = StudentRequestForm(instance=student_request)
    
    return render(request, 'students/edit_request.html', {'form': form, 'request': student_request})


@login_required
def personality_tests(request):
    """آزمون‌های شخصیتی"""
    tests = PersonalityTest.objects.filter(is_active=True)
    completed_tests = StudentTestResult.objects.filter(student=request.user).values_list('test_id', flat=True)
    
    return render(request, 'students/tests.html', {
        'tests': tests,
        'completed_tests': completed_tests
    })


@login_required
def take_test(request, test_id):
    """شرکت در آزمون"""
    test = get_object_or_404(PersonalityTest, id=test_id, is_active=True)
    
    # بررسی اینکه آیا دانشجو قبلاً در این آزمون شرکت کرده یا نه
    if StudentTestResult.objects.filter(student=request.user, test=test).exists():
        messages.warning(request, 'شما قبلاً در این آزمون شرکت کرده‌اید!')
        return redirect('students:tests')
    
    if request.method == 'POST':
        # در اینجا منطق آزمون پیاده‌سازی می‌شود
        # برای سادگی، یک نمره تصادفی تولید می‌کنیم
        import random
        score = random.uniform(60, 100)
        
        StudentTestResult.objects.create(
            student=request.user,
            test=test,
            score=score,
            result_data={'score': score, 'answers': []}
        )
        
        messages.success(request, 'آزمون با موفقیت تکمیل شد!')
        return redirect('students:tests')
    
    return render(request, 'students/take_test.html', {'test': test})


@login_required
def student_files(request):
    """فایل‌های دانشجو"""
    files = StudentFile.objects.filter(student=request.user)
    return render(request, 'students/files.html', {'files': files})


@login_required
def upload_file(request):
    """آپلود فایل"""
    if request.method == 'POST':
        form = StudentFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.student = request.user
            file_obj.save()
            messages.success(request, 'فایل با موفقیت آپلود شد!')
            return redirect('students:files')
    else:
        form = StudentFileForm()
    
    return render(request, 'students/upload_file.html', {'form': form})


@login_required
def student_verification(request):
    """احراز هویت دانشجویی"""
    try:
        profile = request.user.student_profile
    except StudentProfile.DoesNotExist:
        messages.error(request, 'ابتدا پروفایل دانشجویی خود را تکمیل کنید!')
        return redirect('students:profile')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'اطلاعات احراز هویت ارسال شد!')
            return redirect('students:verification')
    else:
        form = StudentProfileForm(instance=profile)
    
    return render(request, 'students/verification.html', {'form': form, 'profile': profile})
