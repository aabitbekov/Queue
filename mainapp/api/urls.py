from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('cities/', views.CityListView.as_view(), name='cities'), # Get all citites with id

    path('departments/', views.DepartmentListView.as_view(), name='deparments'), # Get all departments with id and city_id
    path('departments/<pk>/', views.DepartmentDetailListView.as_view(), name='department_detail'), # Get all department data by id

    path('search/applicant/<app_number>/', views.SearchApplicantView.as_view()), # Search applicant from anoter API or from DATABASE


    path('applicant/', views.ApplicantListView.as_view(), name='applicant'), # Get all applicats data
    path('applicant/<pk>/', views.ApplicantDetailListView.as_view(), name='applicant_detail'), # Get applicat data by id

    path('exams/', views.ExamListView.as_view(), name='exam'), # Get all exams where applicants count less than capacity and date more than today
    path('exam/<department_id>', views.ExamListByDepartmentView.as_view(), name='exam'), # Same as previos but by department id
    path('exam/detail/<pk>/', views.ExamDetailListView.as_view(), name='exam_detail'), # Get exam data by id with applicants list
    path('exam/enroll/queue/', views.ExamEnrollView.as_view()), # Enroll to exam POST

    # path('exam/', views.ExamListView.as_view(), name='exam_list'),
    # path('exam/<pk>/', views.ExamDetailView.as_view(), name='exam_detail'),
]