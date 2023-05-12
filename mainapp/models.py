from django.db import models
from django.core.validators import MinLengthValidator
from django.utils import timezone
from datetime import date, timedelta
from django.core.validators import MinValueValidator, MaxValueValidator


class City(models.Model):
    name = models.CharField(max_length=36, verbose_name='Город', unique=True)

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
    
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=72, verbose_name='ЦОН', unique=True)
    address = models.CharField(max_length=72, verbose_name='Адрес местонахождения', default='')
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='Город')
    haveAutodrom = models.BooleanField(default=False, verbose_name="Автодром") 
    haveExamClass = models.BooleanField(default=False, verbose_name="Экзаменационный класс")
    capacity = models.IntegerField(verbose_name="Вместимость", default=0)

    class Meta:
        verbose_name = 'СпецЦОН'
        verbose_name_plural = 'СпецЦОНы'

    def __str__(self):
        return f'{self.city} , {self.name}'


class Applicant(models.Model):
    class Category(models.TextChoices):
        A = 'A', 'A'
        A1 = 'A1', 'A1' 


    iin = models.CharField(max_length=12, verbose_name='ИИН', unique=True, validators=[MinLengthValidator(12)])
    fullname = models.CharField(max_length=150, verbose_name='ФИО')
    app_number = models.CharField(max_length=12, verbose_name='Номер заявки', unique=True, validators=[MinLengthValidator(12)])
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    service = models.CharField(max_length=150, verbose_name='Тип услуги')
    statusT = models.BooleanField(default=False, verbose_name="Статус ТЭ") 
    statusP = models.BooleanField(default=False, verbose_name="Статус ПЭ") 
    kpp = models.CharField(max_length=12, verbose_name="КПП")
    category =  models.CharField(max_length=2, verbose_name="Категория", choices=Category.choices, default=Category.A1)
    class Meta:
        verbose_name = 'Заявитель'
        verbose_name_plural = 'Заявители'

    
    def __str__(self):
        return f'{self.app_number} , {self.fullname}'


class Exam(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    date = models.DateField(verbose_name="Дата", validators=[MinValueValidator(date.today()), MaxValueValidator(date.today() + timedelta(days=14))])
    time = models.TimeField(verbose_name="Время", default="9:00")
    applicants = models.ManyToManyField(Applicant, blank=True, verbose_name="Участники")
    
    class Meta:
        verbose_name = 'Экзамен (теория)'
        verbose_name_plural = 'Экзамены (теория)'
    
    def has_available_spots(self):
        num_students = self.applicants.count()
        return num_students < self.capacity

    def __str__(self):
        return f'{self.department} , {self.date}, {self.time}'



class Auto(models.Model):
    class Category(models.TextChoices):
        A = 'A', 'A'
        A1 = 'A1', 'A1'
        B = 'B', 'B'
        B1 = 'B1', 'B1'
        C = 'C', 'C'
        C1 = 'C1', 'C1'


    class Transmission(models.TextChoices):
        MKPP = 'MT', 'Механика'
        AKPP = 'AT', 'АКПП'
        none = 'NO', 'Другое'


    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="СпецЦОН")
    mark = models.CharField(max_length=56, verbose_name="Марка авто")
    model = models.CharField(max_length=56, verbose_name="Модель авто")
    grnz = models.CharField(max_length=8, verbose_name="ГРНЗ")
    category =  models.CharField(max_length=2, verbose_name="Категория", choices=Category.choices, default=Category.A1)
    transmission = models.CharField(max_length=2,verbose_name="КПП",
                    choices=Transmission.choices,
                    default=Transmission.AKPP)
    status = models.BooleanField(verbose_name='Исправен', default=True)
    class Meta:
        verbose_name = 'Авто'
        verbose_name_plural = 'Авто'

    def __str__(self):
        return f"{self.department}, {self.mark}, {self.model}"


class PracticeExam(models.Model):
    auto = models.ForeignKey(Auto, on_delete=models.CASCADE, verbose_name="Авто")
    date = models.DateField(verbose_name="Дата", validators=[MinValueValidator(date.today()), MaxValueValidator(date.today() + timedelta(days=14))])
    time = models.TimeField(verbose_name="Время", default="9:00")
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, verbose_name="Заявитель")

    class Meta:
        verbose_name = 'Экзамен (практика)'
        verbose_name_plural = 'Экзамены (практика)'

    def __str__(self):
        return f'{self.auto.department.name} , {self.date}, {self.time}, {self.applicant.iin}'