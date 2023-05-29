from datetime import datetime, timedelta
from mainapp.models import PracticeExam

def check_active_practice_exams(iin):
    now = datetime.now() + timedelta(hours=6)
    active_exams = PracticeExam.objects.filter(date__gte=now.date(), applicant__iin=iin).exists()
    return active_exams


def check_count_exams(iin):
    now = datetime.now() + timedelta(hours=6)
    today_exams = PracticeExam.objects.filter(applicant__iin=iin, date=now.date(), time__lt=now.time())
    past_exams = PracticeExam.objects.filter(applicant__iin=iin, date__lt=now.date()).order_by('date')
    if len(today_exams) + len(past_exams) < 3:
        return {'error': 'Null'}
    else:
        return {'error': 'Applicant have more than 3 attemps.'}
    


def check_past_exams(iin):
    now = datetime.now() + timedelta(hours=6)
    today_exams = PracticeExam.objects.filter(applicant__iin=iin, date=now.date(), time__lt=now.time())
    past_exams = PracticeExam.objects.filter(applicant__iin=iin, date__lt=now.date()).order_by('date')
    if today_exams:
        return now.date() + timedelta(days=7)
    elif past_exams:
        return past_exams[0].date + timedelta(days=7)
    else:
        return now.date()
        


