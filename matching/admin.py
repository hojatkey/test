from django.contrib import admin
from .models import Match, MatchCriteria, MatchHistory


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'job_request', 'match_score', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('student__first_name', 'student__last_name', 'company__company_profile__company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MatchCriteria)
class MatchCriteriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('match', 'action', 'user', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('match__student__first_name', 'match__company__company_profile__company_name')
    readonly_fields = ('created_at',)
