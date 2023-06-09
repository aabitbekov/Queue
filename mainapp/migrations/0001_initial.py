# Generated by Django 4.2 on 2023-05-24 04:01

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import mainapp.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Applicant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('iin', models.CharField(max_length=12, unique=True, validators=[django.core.validators.MinLengthValidator(12)], verbose_name='ИИН')),
                ('fullname', models.CharField(max_length=150, verbose_name='ФИО')),
                ('app_number', models.CharField(max_length=12, unique=True, validators=[django.core.validators.MinLengthValidator(12)], verbose_name='Номер заявки')),
                ('service', models.CharField(max_length=150, verbose_name='Тип услуги')),
                ('statusT', models.BooleanField(default=False, verbose_name='Статус ТЭ')),
                ('statusP', models.BooleanField(default=False, verbose_name='Статус ПЭ')),
                ('kpp', models.CharField(max_length=12, verbose_name='КПП')),
                ('category', models.CharField(max_length=8, verbose_name='Категория')),
                ('phone_number', mainapp.models.KazakhstanPhoneField(blank=True, max_length=12, null=True, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Заявитель',
                'verbose_name_plural': 'Заявители',
            },
        ),
        migrations.CreateModel(
            name='Auto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mark', models.CharField(max_length=56, verbose_name='Марка авто')),
                ('model', models.CharField(max_length=56, verbose_name='Модель авто')),
                ('grnz', models.CharField(max_length=8, verbose_name='ГРНЗ')),
                ('category', models.CharField(choices=[('A1', 'A1'), ('B1', 'B1'), ('A', 'A'), ('B', 'B'), ('C1', 'C1'), ('C', 'C'), ('D1', 'D1'), ('D', 'D'), ('BE', 'BE'), ('C1E', 'C1E'), ('CE', 'CE'), ('D1E', 'D1E'), ('DE', 'DE')], default='A1', max_length=3, verbose_name='Категория')),
                ('transmission', models.CharField(choices=[('MT', 'Механика'), ('AT', 'АКПП')], default='AT', max_length=2, verbose_name='КПП')),
                ('status', models.BooleanField(default=True, verbose_name='Исправен')),
            ],
            options={
                'verbose_name': 'Авто',
                'verbose_name_plural': 'Авто',
            },
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=36, unique=True, verbose_name='Город')),
            ],
            options={
                'verbose_name': 'Город',
                'verbose_name_plural': 'Города',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('code', models.CharField(max_length=16, primary_key=True, serialize=False, verbose_name='Код Цона')),
                ('name', models.CharField(max_length=72, unique=True, verbose_name='ЦОН')),
                ('address', models.CharField(default='', max_length=72, verbose_name='Адрес местонахождения')),
                ('haveAutodrom', models.BooleanField(default=False, verbose_name='Автодром')),
                ('haveExamClass', models.BooleanField(default=False, verbose_name='Экзаменационный класс')),
                ('capacity', models.IntegerField(default=0, verbose_name='Вместимость')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.city', verbose_name='Город')),
            ],
            options={
                'verbose_name': 'СпецЦОН',
                'verbose_name_plural': 'СпецЦОНы',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.department', verbose_name='Департамент')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Профиль пользователя',
                'verbose_name_plural': 'Профили пользователей',
            },
        ),
        migrations.CreateModel(
            name='PracticeExam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 24)), django.core.validators.MaxValueValidator(datetime.date(2023, 6, 7))], verbose_name='Дата')),
                ('time', models.TimeField(default='9:00', verbose_name='Время')),
                ('applicant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.applicant', verbose_name='Заявитель')),
                ('auto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.auto', verbose_name='Авто')),
            ],
            options={
                'verbose_name': 'Экзамен (практика)',
                'verbose_name_plural': 'Экзамены (практика)',
            },
        ),
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 24)), django.core.validators.MaxValueValidator(datetime.date(2023, 6, 7))], verbose_name='Дата')),
                ('time', models.TimeField(default='9:00', verbose_name='Время')),
                ('applicants', models.ManyToManyField(blank=True, to='mainapp.applicant', verbose_name='Участники')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.department', verbose_name='СпецЦОН')),
            ],
            options={
                'verbose_name': 'Экзамен (теория)',
                'verbose_name_plural': 'Экзамены (теория)',
            },
        ),
        migrations.AddField(
            model_name='auto',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.department', verbose_name='СпецЦОН'),
        ),
        migrations.AddField(
            model_name='applicant',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.department', verbose_name='СпецЦОН'),
        ),
    ]
