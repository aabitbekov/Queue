# Generated by Django 4.2 on 2023-05-16 11:33

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_alter_applicant_category_alter_auto_transmission_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 16)), django.core.validators.MaxValueValidator(datetime.date(2023, 5, 30))], verbose_name='Дата'),
        ),
        migrations.AlterField(
            model_name='practiceexam',
            name='applicant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mainapp.applicant', verbose_name='Заявитель'),
        ),
        migrations.AlterField(
            model_name='practiceexam',
            name='date',
            field=models.DateField(validators=[django.core.validators.MinValueValidator(datetime.date(2023, 5, 16)), django.core.validators.MaxValueValidator(datetime.date(2023, 5, 30))], verbose_name='Дата'),
        ),
    ]