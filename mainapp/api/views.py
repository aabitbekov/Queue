from rest_framework import generics
from mainapp.models import Applicant, Department, Exam, City, PracticeExam
from mainapp.api.serializers import *
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


class ApplicantListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer


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
        end_date = start_date + timezone.timedelta(week=25)
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
            return HttpResponse(json_data)
        return Response({'find': False})


class ExamEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            exam = get_object_or_404(Exam, pk=request.data['exam_id'])
        except Http404:
             return JsonResponse({'error': 'Exam not found.'}, status=404)
        try:
            app = get_object_or_404(Applicant, pk=request.data['user_id'])
        except Http404:
             return JsonResponse({'error': 'Applicant not found.'}, status=404)
        if app.statusT:
             return Response({"error": "Нельзя добавлять заявителей со положительным статусом тоеритического экзамена к тоеритическому экзамену."},
                                                                                                           status=status.HTTP_400_BAD_REQUEST)
        exam.applicants.add(applicant)
        return Response({'enrolled': True})


class CarsListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AutoSerializer
    queryset = Auto.objects.all()

class PracticeExamListViewByDepartmentAndCategory(APIView):
    def post(self, request):
        try:
            dep_id = get_object_or_404(Department, pk=request.data['department_id'])
        except Http404:
            error_message = 'Department not found.'  # Customize the error message as desired
            return JsonResponse({'error': error_message}, status=404)
        tomorrow = date.today() + timedelta(days=1)
        category = request.data['category']  # add functions for double of more category
        kpp = request.data['kpp']
        practice_exams = PracticeExam.objects.filter(
                Q(auto__department_id=dep_id) & 
                Q(auto__category=category) & 
                Q(auto__transmission=kpp) & 
                Q(applicant__isnull=True) &
                Q(date__gte=tomorrow))
        serializer = PracticeExamSerializer(practice_exams, many=True)
        return Response(serializer.data)


class PracticeExamListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PracticeExam.objects.filter(applicant=None)
    serializer_class = PracticeExamSerializer 


class PractcieExamEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            exam = get_object_or_404(PracticeExam, pk=request.data['exam_id'])
        except Http404:
            return JsonResponse({'error': 'Exam not found.'}, status=404)
        try:
            app = get_object_or_404(Applicant, pk=request.data['user_id'])
        except Http404:
             return JsonResponse({'error': 'Applicant not found.'}, status=404)

        if app.statusT:
            exam.applicant = app
            exam.save()
            return Response({'enrolled': True})
        else:
            return Response({"error": "Нельзя добавлять заявителей со отрицательным статусом тоеритического экзамена к практическому экзамену."},
                                status=status.HTTP_400_BAD_REQUEST)


    
