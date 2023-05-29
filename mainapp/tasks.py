from celery import shared_task
from datetime import datetime, time, timedelta, date
from django.utils import timezone
from .models import *
import requests
import json


@shared_task
def clean_exams():
    today = date.today()
    exams_to_delete = PracticeExam.objects.filter(date__lt=today)
    exams_to_delete.delete()


@shared_task
def clean_practice_exams():
    today = date.today()
    exams_to_delete = PracticeExam.objects.filter(date__lt=today)
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
def generate_practice_exams(): 
    cars = Auto.objects.filter(status=True) 
    last_exam = PracticeExam.objects.order_by('-date').first()
    if last_exam:
        starting_datetime = last_exam.date + timedelta(days=7 - last_exam.date.weekday())
    else:
        now = timezone.now() 
        starting_datetime = now + timedelta(days=1)  
    starting_time = time(hour=9) 
    exam_date = starting_datetime.date()  # Start from tomorrow
    while exam_date.weekday() != 6:  # Continue until Saturday (weekday 6)
        for car in cars: 
            exam_time = datetime.combine(exam_date, starting_time) 
            while exam_time.time() < time(hour=17 if exam_date.weekday() != 5 else 12):  # End at 5:00 PM each day
                exam = PracticeExam.objects.create(auto=car, date=exam_date, time=exam_time.time()) 
                exam_time += timedelta(minutes=15)
        exam_date += timedelta(days=1)  # Move to the next day

@shared_task
def generate_practice_exams_180days(): 
    cars = Auto.objects.filter(status=True) 
    now = timezone.now() 
    starting_datetime = now + timedelta(days=1)  
    starting_time = time(hour=9) 
    exam_date = starting_datetime.date()  # Start from tomorrow
    end_date = exam_date + timedelta(days=180)  # End after 180 days
    while exam_date <= end_date:  # Continue until end date
        if exam_date.weekday() != 6:  # Exclude Sunday (weekday 6)
            for car in cars: 
                exam_time = datetime.combine(exam_date, starting_time) 
                while exam_time.time() < time(hour=17 if exam_date.weekday() != 5 else 12):  # End at 5:00 PM each day
                    exam = PracticeExam.objects.create(auto=car, date=exam_date, time=exam_time.time()) 
                    exam_time += timedelta(minutes=15)
        exam_date += timedelta(days=1)  # Move to the next day


@shared_task
def getTokenForSMSGateway():
    url = "https://idp-iis.gov4c.kz/auth/realms/con-web/protocol/openid-connect/token"          
    payload = 'username=robot_ekc&password=j1k65dF3%2612!&client_id=cw-web&grant_type=password'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic Og=='
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result=response.text
    access_token=result.split('"')[3]
    refresh_token=result.split('"')[11]
    try:
        token = GatewayToken.objects.get(id=1)
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.save()
    except:
        GatewayToken(id=1, access_token=access_token, refresh_token=refresh_token).save()


@shared_task
def getTokenForBMGGateway():
    url = "https://idp-iis.gov4c.kz/auth/realms/con-web/protocol/openid-connect/token"          #idp.gov4c.kz
    payload = 'username=test-operator&password=DjrsmA9RMXRl&client_id=cw-queue-service&grant_type=password'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic Og=='
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    result=response.text
    access_token=result.split('"')[3]
    refresh_token=result.split('"')[11]
    try:
        token = GatewayToken.objects.get(id=2)
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.save()
    except:
        GatewayToken(id=2, access_token=access_token, refresh_token=refresh_token).save()


@shared_task
def getTokenForTExamGateway():
    url = 'https://idp-iis.gov4c.kz/auth/realms/con-web/protocol/openid-connect/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'username': 'test-operator',
        'password': 'DjrsmA9RMXRl',
        'client_id': 'cw-queue-service',
        'grant_type': 'password'
    }
    response = requests.post(url, headers=headers, data=data)
    access_token=response.text.split('"')[3]
    refresh_token=response.text.split('"')[11]
    try:
        token = GatewayToken.objects.get(id=3)
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.save()
    except:
        GatewayToken(id=3, access_token=access_token, refresh_token=refresh_token).save()


@shared_task
def getPhoneNumberFromBMG(iin):
    bmg_access_token = GatewayToken.objects.get(id=2)
    bmg_access_token = bmg_access_token.access_token
    url = "https://api35-iis.gov4c.kz:30138/api/bmg/check/" + iin    
    payload = {}
    headers = {
    'Authorization': 'Bearer '+ bmg_access_token
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    if data['isExists'] == False or data['error'] != False:
        return False
    else:
        return data['phone']


@shared_task
def send_sms(phone_number, message):
    sms_gateway_token = GatewayToken.objects.get(id=1).access_token
    url = "https://api42-iis.gov4c.kz:30138/api/smsgateway/send"  
    payload = json.dumps({
    "phone": phone_number,
    "smsText": message
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer '+ sms_gateway_token
    }
    requests.request("POST", url, headers=headers, data=payload)


@shared_task
def BrokenCars():
    now = timezone.now() + timedelta(hours=6)
    exams = PracticeExam.objects.filter(date=now, status='С')
    saturday = now.date() + timedelta(days=5 - now.weekday())
    for exam in exams:    
        for i in range(5):
            saturday += timedelta(days=i*7) 
            saturday_exam = PracticeExam.objects.filter(date=saturday, auto=exam.auto, applicant__isnull=True).order_by('time').first()
            if saturday_exam:
                saturday_exam.applicant = exam.applicant
                saturday_exam.save()
                # exam.delete()
                send_sms.delay(exam.applicant.phone_number, f"Вас успешно записали на практический экзамен дата {saturday_exam.date} {saturday_exam.time}. Ждем вас по адресу {saturday_exam.auto.department.address}")


def getTheoryResults(iin):
    token = GatewayToken.objects.get(id=3).access_token
    url = "http://10.51.203.172:8080/getInfoPDD"        #bmg.gov4c.kz 
    payload = json.dumps({ 
    "iin": iin 
    }) 
    headers = { 
        'Content-Type': 'application/json', 
        'Authorization': 'Bearer '+ token 
    } 
    response = requests.request("POST", url, headers=headers, data=payload) 

    if response.text.find('NO information for IIN')!=-1: 
        return False
    
    else: 
        data_arr = response.json() 
        for d in data_arr: 
            data=json.loads(json.dumps(d)[1:-1:1]) 
            iin = data["iin"] 
            department_id = data["code_center"] 
            category = data["category"] 
            statusT = data["result_test"] 
            if statusT == "passed":
                statusT = True
                return [department_id, category, statusT]
        return False
    

