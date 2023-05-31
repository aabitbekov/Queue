# Generated by Django 4.2 on 2023-05-30 03:37

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0007_alter_exam_date_alter_practiceexam_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 30)), django.core.validators.MaxValueValidator(datetime.date(2024, 5, 29))], verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='practiceexam',
            name='date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 30)), django.core.validators.MaxValueValidator(datetime.date(2024, 5, 29))], verbose_name='Дата'),
        ),
    ]
