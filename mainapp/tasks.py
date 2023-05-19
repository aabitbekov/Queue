from celery import shared_task
from datetime import datetime, time, timedelta, date
from django.utils import timezone
from .models import *

@shared_task
def clean_exams():
    today = date.today()
    exams_to_delete = Exam.objects.filter(date__lt=today)
    exams_to_delete.delete()


@shared_task
def generate_exams():
    departments = Department.objects.all()
    now = timezone.now()
    starting_datetime = now + timedelta(days=1) 
    starting_time = time(hour=9)
    n = 0 
    for department in departments:
        n = 0 
        for i in range(starting_datetime.weekday(), 6):
            exam_date = starting_datetime.date() + timedelta(days=n)
            exam_time = datetime.combine(exam_date, starting_time)
            n += 1
            while exam_time.time() < time(hour=18 if i != 5 else 13):
                Exam.objects.create(department=department, date=exam_date, time=exam_time.time())
                exam_time += timedelta(minutes=40)


@shared_task
def clean_exams():
    today = date.today()
    exams_to_delete = PracticeExam.objects.filter(date__lt=today)
    exams_to_delete.delete()


@shared_task
def generate_practice_exams():
    cars = Auto.objects.filter(status=True)
    now = timezone.now()
    starting_datetime = now + timedelta(days=1) 
    starting_time = time(hour=9)
    for i in range(5):
        exam_date = starting_datetime.date() + timedelta(days=i)
        for car in cars:
            exam_time = datetime.combine(exam_date, starting_time)
            while exam_time.time() < time(hour=17 if i != 5 else 15):
                exam = PracticeExam.objects.create(auto=car, date=exam_date, time=exam_time.time())
                exam_time += timedelta(minutes=15)


@shared_task
def send_sms(phone_number, message):
    print(f"To {phone_number} message: {message}")


    


# @shared_task
# def generate_exams():

# departments = Department.objects.all()
# now = timezone.now()
# starting_datetime = now + timedelta(days=1) 
# starting_time = time(hour=9)
# n = 0 
# for department in departments:
#     n = 0 
#     for i in range(starting_datetime.weekday(), 6):
#         exam_date = starting_datetime.date() + timedelta(days=n)
#         exam_time = datetime.combine(exam_date, starting_time)
#         n += 1
#         while exam_time.time() < time(hour=18 if i != 5 else 13):
#             Exam.objects.create(department=department, date=exam_date, time=exam_time.time())
#             exam_time += timedelta(minutes=40)






# cars = Auto.objects.filter(status=True)
# now = timezone.now()
# starting_datetime = now + timedelta(days=1) 
# starting_time = time(hour=9)
# for i in range(5):
#     exam_date = starting_datetime.date() + timedelta(days=i)
#     for car in cars:
#         exam_time = datetime.combine(exam_date, starting_time)
#         while exam_time.time() < time(hour=18):
#             exam = PracticeExam.objects.create(auto=car, date=exam_date, time=exam_time.time())
#             exam_time += timedelta(minutes=15)