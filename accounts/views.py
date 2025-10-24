from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def home(request):
    """صفحه اصلی"""
    return render(request, 'home.html')


def register(request):
    """ثبت نام کاربر"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'ثبت نام با موفقیت انجام شد!')
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """ورود کاربر"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, 'ورود با موفقیت انجام شد!')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است!')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """خروج کاربر"""
    logout(request)
    messages.success(request, 'خروج با موفقیت انجام شد!')
    return redirect('accounts:home')


@login_required
def dashboard(request):
    """داشبورد کاربر"""
    user = request.user
    
    if user.user_type == 'student':
        return render(request, 'students/dashboard.html', {'user': user})
    elif user.user_type == 'company':
        return render(request, 'companies/dashboard.html', {'user': user})
    else:
        return render(request, 'admin/dashboard.html', {'user': user})


@login_required
def profile(request):
    """پروفایل کاربر"""
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    """ویرایش پروفایل کاربر"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'پروفایل با موفقیت به‌روزرسانی شد!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})
