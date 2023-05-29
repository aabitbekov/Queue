from rest_framework import generics
from mainapp.models import *
from mainapp.api.serializers import *
from rest_framework.response import Response
from django.db.models import Count
from django.http import JsonResponse
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.db.models import Count, F, Q
from django.utils import timezone
from django.http import Http404
from mainapp.tasks import *
import random
from .getMainCategory import getMainCategory
from .checkers import check_active_practice_exams, check_past_exams, check_count_exams

class PhoneNumberVerificationView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, iin):
        phone_number = getPhoneNumberFromBMG(iin)
        if phone_number == False:
            return Response({'error': 'Заявитель с таким иин не найден.'}, status=200)
        code = random.randint(100000, 999999)
        if VerifySMS.objects.filter(iin=iin).exists():
            verify = VerifySMS.objects.get(iin=iin)
            verify.code = code
            verify.save()
        else:
            VerifySMS(iin=iin, code=code, phone_number=phone_number).save()
        task = send_sms.delay(phone_number, message=f'Ваш код для авторизации {code}')  
        return Response({'success': True}, status=200)



class CodeVerificationView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = VerifySMS.objects.get(iin=request.data['iin'])
            if user.code == request.data['code']:
                res = getTheoryResults(request.data['iin'])
                if res == False:
                    return Response({'error': 'Заявитель не сдал теоритический экзамен'}, status=200)
                department_id = res[0]
                category = res[1]
                statusT = res[2]
                if statusT:
                    dep = Department.objects.get(id=department_id)
                    category = getMainCategory(category)
                    try:
                        applicant = Applicant.objects.get(iin=user.iin)
                        if applicant.statusT != statusT:
                            applicant.department.id = department_id
                            applicant.statusT = statusT
                            applicant.category = category
                            applicant.save
                    except Applicant.DoesNotExist:
                        applicant = Applicant.objects.get_or_create(iin=user.iin, department=dep, statusT=statusT, statusP=False, kpp="MT", category=category, phone_number=user.phone_number)
                    return Response({
                        "id" : applicant.id,
                        "iin" : applicant.iin,
                        "department_id" : applicant.department.id,
                        "city" : dep.city.name,
                        "department" : dep.name,
                        "category" : applicant.category
                        })
                else:
                    return Response({'error': 'Заявитель не сдал теоритический экзамен'}, status=200)

            else:
                return Response({"success": False})
        except VerifySMS.DoesNotExist:
            return Response({'error': 'user not found.'}, status=200)
        


class PracticeExamListViewByDepartmentAndCategory(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            dep = get_object_or_404(Department, pk=request.data['department_id'])
        except Http404:
            return Response({'error': 'Department not found.' }, status=404)
        
        try:
            app = Applicant.objects.get(iin=request.data['iin'])
        except Applicant.DoesNotExist:
            return Response({'error': 'Applicant not found.'}, status=404)
    
        #First Checker
        if check_active_practice_exams(app.iin):
            return Response({'error': 'Applicant have active exam.'}, status=200)
        else:
            #Second Checker
            res = check_count_exams(app.iin)
            if res['error'] != 'Null':
                return Response(res, status=200)
            else:
                tomorrow = check_past_exams(app.iin)

        kpp = request.data['kpp'] # MT or AT
        if kpp != app.kpp:
            app.kpp == kpp
            app.save()
        category = getMainCategory(request.data['category'])
        # practice_exams = PracticeExam.objects.extra(where=["EXTRACT (DOW FROM date) != 6"])
        practice_exams = PracticeExam.objects.filter(
                Q(auto__department_id=dep.id) & 
                Q(auto__category=category) & 
                Q(auto__transmission=kpp) & 
                Q(applicant__isnull=True) &
                Q(date__gte=tomorrow)
                )
        serializer = PracticeExamSerializer(practice_exams, many=True)
        return Response(serializer.data)



class PractcieExamEnrollView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            exam = get_object_or_404(PracticeExam, pk=request.data['exam_id'])
        except Http404:
            return JsonResponse({'error': 'Exam not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            app = get_object_or_404(Applicant, pk=request.data['user_id'])
        except Http404:
             return JsonResponse({'error': 'Applicant not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if exam.applicant:
            return JsonResponse({'error': 'Exam not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if app.statusT:
            now = datetime.now() + timedelta(hours=6)
            if check_active_practice_exams(app.iin):
                return Response({"error": "У заявителя есть активные экзамены."},
                                status=status.HTTP_400_BAD_REQUEST)
            elif check_past_exams(app.iin) != now.date():
                return Response({"error": "У заявителя есть активные экзамены.Прошу выбрать подходящее время.(После проваленной попытки заявитель в течении 7 дней не может быть допущен к экзамену)"},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                exam.applicant = app
                exam.save()
                
                # print(app.phone_number, f"Вы успешно записались на практический экзамен дата {exam.date} {exam.time}. Ждем вас по адресу {exam.auto.department.address}")
                send_sms.delay(app.phone_number, f"Вы успешно записались на практический экзамен дата {exam.date} {exam.time}. Ждем вас по адресу {exam.auto.department.address}")
                return Response({'enrolled': True})
        else:
            return Response({"error": "Нельзя добавлять заявителей со отрицательным статусом тоеритического экзамена к практическому экзамену."},
                                status=status.HTTP_400_BAD_REQUEST)
        

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
        end_date = start_date + timezone.timedelta(weeks=25)
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
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, iin):
        try:
            applicant = Applicant.objects.get(iin=iin)
        except:
            return Response({'find': False})
        if applicant:
             return Response({
          'id' : applicant.id,
          'iin': applicant.iin,
          'city': applicant.department.city.name,
          'department': applicant.department.name, 
          'department_code': applicant.department.id, 
          'statusT': applicant.statusT, 
          'statusP': applicant.statusP, 
          'kpp': applicant.kpp, 
          'category': applicant.category
        }) 


class CarsListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AutoSerializer
    queryset = Auto.objects.all()



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
        
        
        if Exam.objects.filter(Q(applicants__iin=app.iin) & Q(date=exam.date)).exists(): # Проверка записан ли пользаватель на тот же день
            return Response({'Вы уже записаны': True})

        # Проверки на запись на тоерию

        exam.applicants.add(app)
        return Response({'enrolled': True})



class PracticeExamListView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PracticeExam.objects.filter(applicant=None)
    serializer_class = PracticeExamSerializer 




class TodayPracticeExamListView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, department_id):
        now = datetime.now() + timedelta(hours=6)
        exams = PracticeExam.objects.filter(
                 auto__department=department_id, date=now.date()
             )
        print(exams)
        exams = PracticeExamDetailSerializer(exams, many=True)
        return Response(
          exams.data
        )
