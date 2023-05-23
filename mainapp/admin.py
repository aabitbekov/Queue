from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import date


class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        if not change:  # Only execute on user creation
            obj.is_staff = True  # Set is_staff to True
        super().save_model(request, obj, form, change)



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['id']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['city', 'name']
    search_fields = ['name']
    list_filter = ['haveAutodrom', 'haveExamClass', 'capacity']
    ordering = ['city']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Для суперпользователя отображаем все данные
        return qs.filter(id=request.user.profile.department.id)

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['iin', 'fullname', 'department', 'service']
    list_filter = ['iin', 'app_number', 'department', 'service']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Для суперпользователя отображаем все данные
        return qs.filter(department_id=request.user.profile.department.id)

class ExamAdmin(admin.ModelAdmin):
    list_display = ['department', 'date', 'time']
    search_fields = ['applicants', 'department']
    list_filter = ['department', 'date', 'time']
    ordering = ['-date']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Для суперпользователя отображаем все данные
        return qs.filter(Q(department_id=request.user.profile.department.id) &
                        Q(date=date.today()))

class PracticeExamAdmin(admin.ModelAdmin):
    # search_fields = ['applicant.iin', 'auto.department.name']
    list_display = ['auto_department', 'date', 'time', 'applicant', 'auto']
    list_filter = ['time', 'applicant']

    def auto_department(self, obj):
        return obj.auto.department.name
    
    auto_department.short_description = 'ЦОН'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Для суперпользователя отображаем все данные
        return qs.filter(Q(auto__department_id=request.user.profile.department.id) &
                        Q(date=date.today()))
    

class AutoAdmin(admin.ModelAdmin):
    list_display = ['department', 'model', 'transmission', 'grnz', 'category']
    list_filter = ['department', 'grnz', 'category']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs  # Для суперпользователя отображаем все данные
        return qs.filter(department_id=request.user.profile.department.id)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']
    list_filter = ['department']


# Register your models here.
admin.site.register(City, CityAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Auto, AutoAdmin)
admin.site.register(PracticeExam, PracticeExamAdmin)
admin.site.register(UserProfile, UserProfileAdmin)