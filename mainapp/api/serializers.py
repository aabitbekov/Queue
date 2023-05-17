from rest_framework import serializers
from mainapp.models import *


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'city']


class DepartmentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'
        

class DepartmentSerializerForExam(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name']


class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Applicant
        fields = '__all__'


class ExamListSerializer(serializers.ModelSerializer):
    exam_date = serializers.DateField(source='date')
    class Meta:
        model = Exam
        fields = ['id', 'exam_date', 'time', 'department']



class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = '__all__'


class ExamDetailSerializer(serializers.ModelSerializer):
    department = DepartmentSerializerForExam(many=False, read_only=True)
    applicants = ApplicantSerializer(many=True, read_only=False)

    class Meta:
        model = Exam
        fields = ['date', 'time', 'department', 'applicants']


class PracticeExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = PracticeExam
        fields = '__all__'

class AutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auto
        fields = '__all__'
