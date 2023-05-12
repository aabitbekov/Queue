from rest_framework import generics
from mainapp.models import Applicant, Department, Exam, City
from mainapp.api.serializers import ExamListSerializer, DepartmentDetailSerializer, ApplicantSerializer, ApplicantNumberSerializer, DepartmentSerializer, ExamSerializer, ExamDetailSerializer, CitySerializer
from rest_framework.response import Response
from django.db.models import Count
from django.core import serializers
from django.http import JsonResponse
from rest_framework import status
import json
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import date
from django.db.models import Count, F, Q
from django.utils import timezone

class ApplicantListView(generics.ListAPIView, generics.CreateAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        my_model_instance = serializer.save()
        exams = Exam.objects.filter(department_id=my_model_instance.department.id).order_by('date')
        freeExams = [my_model_instance]
        for exam in exams:
            if exam.applicants.count() != exam.department.capacity:
                freeExams.append(exam)
                
        json_data = serializers.serialize('json', freeExams)
        return HttpResponse(json_data, content_type='application/json')
        # return Response(data=json_data, status=status.HTTP_201_CREATED, content_type='application/json')


class ApplicantDetailListView(generics.RetrieveUpdateAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer


class CityListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = City.objects.all()
    serializer_class = CitySerializer

class DepartmentListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class DepartmentDetailListView(generics.RetrieveUpdateAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Department.objects.all()
    serializer_class = DepartmentDetailSerializer 

class ExamListByDepartmentView(APIView):
    def get(self, request, department_id):
        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=7)
        exams = Exam.objects.annotate(num_applicants=Count('applicants')).filter(
            num_applicants__lt=F('department__capacity'),
            date__range=(start_date, end_date),
            department_id=department_id
            )
        data = []
        for exam in exams:
            exam_data = {
                'id': exam.id,
                'department': exam.department.name,
                'date': exam.date,
                'time': exam.time,
                'applicants_count': exam.num_applicants,
                'capacity': exam.department.capacity,
            }
            data.append(exam_data)
        return Response(data)

class ExamListView(APIView):
    def get(self, request):

        start_date = timezone.now().date()
        end_date = start_date + timezone.timedelta(days=7)
        exams = Exam.objects.annotate(num_applicants=Count('applicants')).filter(
            num_applicants__lt=F('department__capacity'),
            date__range=(start_date, end_date),
            )
        data = []
        for exam in exams:
            exam_data = {
                'id': exam.id,
                'department': exam.department.name,
                'date': exam.date,
                'time': exam.time,
                'applicants_count': exam.num_applicants,
                'capacity': exam.department.capacity,
            }
            data.append(exam_data)
        return Response(data)

class ExamDetailListView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Exam.objects.annotate(num_applicants=Count('applicants')).filter(num_applicants__lt=F('department__capacity'))
    serializer_class = ExamDetailSerializer 


class SearchApplicantView(APIView):
    def get(self, request, app_number):
        # LOGIC FOR FIND APPLICANT FROM IISCON2 API (REQUEST) MUST BE HERE
        applicant = Applicant.objects.filter(app_number=app_number)
        json_data = serializers.serialize('json', applicant)
    
        if applicant:
            return HttpResponse({json_data}, 'json')
        return Response({'find': False})

class ExamEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        exam = get_object_or_404(Exam, pk=request.data['pk'])
        applicant = get_object_or_404(Applicant, pk=request.data['id'])
        # exams = Exam.objects.filter(applicants=)
        exam.applicants.add(applicant)
        return Response({'enrolled': True})








