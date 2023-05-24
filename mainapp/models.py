from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, MinLengthValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=36, verbose_name='Город', unique=True)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
    
    def __str__(self):
        return self.name


class Department(models.Model):
    id = models.CharField(max_length=20, verbose_name="Код Цона", primary_key=True)
    name = models.CharField(max_length=72, verbose_name='ЦОН', unique=True)
    address = models.CharField(max_length=126, verbose_name='Адрес местонахождения', default='')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    haveAutodrom = models.BooleanField(default=False, verbose_name="Автодром") 
    haveExamClass = models.BooleanField(default=False, verbose_name="Экзаменационный класс")
    capacity = models.IntegerField(verbose_name="Вместимость", default=0)

    class Meta:
        verbose_name = 'СпецЦОН'
        verbose_name_plural = 'СпецЦОНы'

    def __str__(self):
        return f'{self.city} , {self.name}'


class KazakhstanPhoneField(models.CharField):
    default_validators = [RegexValidator(
        regex=r'^\+7\d{10}$',
        message="Enter a valid phone number in the format: '+7XXXXXXXXXX'"
    )]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 12  # '+7' + 10 digits
        kwargs['verbose_name'] = 'Номер телефона'
        kwargs['blank'] = True
        kwargs['null'] = True
        super().__init__(*args, **kwargs)




class Applicant(models.Model):
    iin = models.CharField(max_length=12, verbose_name='ИИН', unique=True, validators=[MinLengthValidator(12)])
    fullname = models.CharField(max_length=150, verbose_name='ФИО')
    app_number = models.CharField(max_length=12, verbose_name='Номер заявки', unique=True, validators=[MinLengthValidator(12)])
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    service = models.CharField(max_length=150, verbose_name='Тип услуги')
    statusT = models.BooleanField(default=False, verbose_name="Статус ТЭ") 
    statusP = models.BooleanField(default=False, verbose_name="Статус ПЭ") 
    kpp = models.CharField(max_length=12, verbose_name="КПП")
    category =  models.CharField(max_length=8, verbose_name="Категория")
    phone_number = KazakhstanPhoneField()
    
    class Meta:
        verbose_name = 'Заявитель'
        verbose_name_plural = 'Заявители'

    
    def __str__(self):
        return f'{self.app_number}'


class Exam(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    date = models.DateField(verbose_name="Дата", validators=[MinValueValidator(date.today()), MaxValueValidator(date.today() + timedelta(days=14))])
    time = models.TimeField(verbose_name="Время", default="9:00")
    applicants = models.ManyToManyField(Applicant, blank=True, verbose_name="Участники")
    
    class Meta:
        verbose_name = 'Экзамен (теория)'
        verbose_name_plural = 'Экзамены (теория)'

    def __str__(self):
        return f'{self.department} , {self.date}, {self.time}'



class Auto(models.Model):
    class Category(models.TextChoices):
        A1 = 'A1', 'A1'
        B1 = 'B1', 'B1'
        A = 'A', 'A'
        B = 'B', 'B'
        C1 = 'C1', 'C1'
        C = 'C', 'C'
        D1 = 'D1', 'D1'
        D = 'D' , 'D'
        BE = 'BE' , 'BE'
        C1E = 'C1E' , 'C1E'
        CE = 'CE' , 'CE'
        D1E = 'D1E' , 'D1E'
        DE = 'DE' , 'DE'

    class Transmission(models.TextChoices):
        MKPP = 'MT', 'Механика'
        AKPP = 'AT', 'АКПП'


    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    mark = models.CharField(max_length=56, verbose_name="Марка авто")
    model = models.CharField(max_length=56, verbose_name="Модель авто")
    grnz = models.CharField(max_length=8, verbose_name="ГРНЗ")
    category =  models.CharField(max_length=3, verbose_name="Категория", choices=Category.choices, default=Category.A1)
    transmission = models.CharField(max_length=2,verbose_name="КПП",
                    choices=Transmission.choices,
                    default=Transmission.AKPP)
    status = models.BooleanField(verbose_name='Исправен', default=True)
    class Meta:
        verbose_name = 'Авто'
        verbose_name_plural = 'Авто'

    def __str__(self):
        return f"{self.mark}, {self.model}"


class PracticeExam(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, verbose_name="Авто")
    date = models.DateField(verbose_name="Дата", validators=[MinValueValidator(date.today()), MaxValueValidator(date.today() + timedelta(days=14))])
    time = models.TimeField(verbose_name="Время", default="9:00")
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, verbose_name="Заявитель", null=True, blank=True)

    class Meta:
        verbose_name = 'Экзамен (практика)'
        verbose_name_plural = 'Экзамены (практика)'

    def clean(self):
           super().clean()
           if self.applicant and not self.applicant.statusT:
                raise ValidationError("Нельзя добавлять заявителей со отрицательным статусом тоеритического экзамена к практическому экзамену.")

    def __str__(self):
        return f'{self.auto.department.name} , {self.date}, {self.time}'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name='Департамент')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'{self.user.username}'
    

class GatewayToken(models.Model):
    access_token = models.TextField()
    refresh_token = models.TextField()
    created = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.created = timezone.now()
        return super(GatewayToken, self).save(*args, **kwargs)


class VerifySMS(models.Model):
    iin = models.CharField(max_length=12, verbose_name='ИИН', unique=True, validators=[MinLengthValidator(12)])
    phone_number = KazakhstanPhoneField()
    code = models.CharField(verbose_name="code")
    

    