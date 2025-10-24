from django.contrib import admin
from .models import StudentProfile, StudentRequest, PersonalityTest, StudentTestResult, StudentFile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'university', 'field_of_study', 'degree_level', 'is_student_verified')
    list_filter = ('degree_level', 'is_student_verified', 'university')
    search_fields = ('user__first_name', 'user__last_name', 'university', 'student_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_type', 'work_type', 'field_of_study', 'is_active')
    list_filter = ('job_type', 'work_type', 'is_active', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'field_of_study', 'skills')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PersonalityTest)
class PersonalityTestAdmin(admin.ModelAdmin):
    list_display = ('name', 'test_type', 'is_active', 'created_at')
    list_filter = ('test_type', 'is_active')
    search_fields = ('name', 'description')


@admin.register(StudentTestResult)
class StudentTestResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'test', 'score', 'completed_at')
    list_filter = ('test', 'completed_at')
    search_fields = ('student__first_name', 'student__last_name', 'test__name')
    readonly_fields = ('completed_at',)


@admin.register(StudentFile)
class StudentFileAdmin(admin.ModelAdmin):
    list_display = ('student', 'title', 'file_type', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
    search_fields = ('student__first_name', 'student__last_name', 'title')
    readonly_fields = ('uploaded_at',)
