from django.contrib import admin
from .models import CompanyProfile, JobRequest


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'company_type', 'industry', 'is_verified')
    list_filter = ('company_type', 'industry', 'is_verified')
    search_fields = ('company_name', 'industry', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(JobRequest)
class JobRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'job_type', 'work_type', 'is_active')
    list_filter = ('job_type', 'work_type', 'is_active', 'created_at')
    search_fields = ('title', 'field_of_study', 'required_skills')
    readonly_fields = ('created_at', 'updated_at')
