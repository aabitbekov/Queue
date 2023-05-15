# from celery import shared_task
# from datetime import datetime, time, timedelta
# from django.utils import timezone
# from mainapp.models import Exam, Department


# @shared_task
# def generate_exams():

# departments = Department.objects.all()
# now = timezone.now()
# starting_datetime = now + timedelta(days=(7-now.weekday())) 
# starting_time = time(hour=9)
# for i in range(5):
#     exam_date = starting_datetime.date() + timedelta(days=i)
#     for department in departments:
#         exam_time = datetime.combine(exam_date, starting_time)
#         while exam_time.time() < time(hour=18):
#             exam = Exam.objects.create(department=department, date=exam_date, time=exam_time.time())
#             exam_time += timedelta(hours=1)



# cars = Auto.objects.all()
# now = timezone.now()
# starting_datetime = now + timedelta(days=(7-now.weekday())) 
# starting_time = time(hour=9)
# for i in range(5):
#     exam_date = starting_datetime.date() + timedelta(days=i)
#     for car in cars:
#         exam_time = datetime.combine(exam_date, starting_time)
#         while exam_time.time() < time(hour=18):
#             exam = PracticeExam.objects.create(auto=car, date=exam_date, time=exam_time.time(), applicant_id=1)
#             exam_time += timedelta(minutes=40)