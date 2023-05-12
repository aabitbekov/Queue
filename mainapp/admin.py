from django.contrib import admin

from .models import City, Department, Applicant, Exam, Auto, PracticeExam

class CityAdmin(admin.ModelAdmin):
    search_fields = ['name']
    ordering = ['id']

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['city', 'name']
    search_fields = ['name']
    list_filter = ['haveAutodrom', 'haveExamClass', 'capacity']
    ordering = ['city']

class ApplicantAdmin(admin.ModelAdmin):
    list_display = ['iin', 'fullname', 'department', 'service']
    list_filter = ['iin', 'app_number', 'department', 'service']

class ExamAdmin(admin.ModelAdmin):
    list_display = ['department', 'date', 'time']
    search_fields = ['applicants', 'department']
    list_filter = ['department', 'date', 'time']
    ordering = ['-date']
class PracticeExamAdmin(admin.ModelAdmin):
    # search_fields = ['applicant.iin', 'auto.department.name']
    list_display = ['date', 'time', 'applicant']
    list_filter = ['date', 'time', 'applicant']
    
    # list_filter = ['date', 'auto']


# Register your models here.
admin.site.register(City, CityAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Applicant, ApplicantAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Auto)
admin.site.register(PracticeExam, PracticeExamAdmin)