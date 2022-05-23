from rest_framework import serializers
from django.core import exceptions
from .models import Schedule, SubjectTutor, User, Tutee, Tutor, Subject
import django.contrib.auth.password_validation as password_validators 

import re

class UserSerializer(serializers.ModelSerializer):
	confirm_password = serializers.CharField(write_only=True,  style={'input_type': 'password'})
	class Meta:
		model = User
		fields = ('unique_identifier', 'is_staff', 'is_tutor', 'is_tutee', 'password', 'confirm_password',)
		read_only_fields = ('unique_identifier', 'is_staff', 'is_tutor', 'is_tutee',)
		extra_kwargs = {
			'password': {
				'write_only': True,
				'style': {'input_type': 'password'}
			},
		}

class ResetPasswordEmailSerializer(serializers.Serializer):
	email = serializers.EmailField()
	user_type = serializers.IntegerField()

class ResetPasswordTokenSerializer(serializers.Serializer):
	token = serializers.CharField()
	new_password = serializers.CharField()
	ui64 = serializers.CharField()

	def validate_new_password(self, value):
		try:
			password_validators.validate_password(password=value)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return value

class LogoutSerializer(serializers.Serializer):
	token = serializers.CharField() 


class TuteeRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)

	class Meta:
		model = Tutee
		fields = ('user', 'registration_number', 'email', 'name')
		extra_kwargs = {
			'registration_number': {
				'read_only': True
			}
		}

	def create(self, validated_data):
		registration_number = validated_data['email'][:9]
		unique_identifier = 'tutee' + registration_number

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_tutee = True
		user.save()
		tutee = Tutee.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], name=validated_data['name'])
		return tutee

	def validate_name(self, value):
		normalized_name = value.strip()
		if not re.search("^[a-zA-Zñá-úÁ-Úü]([.](?![.])|[ ](?![ .])|[a-zA-Zñá-úÁ-Úü])*$", normalized_name):
			raise serializers.ValidationError("Name must be valid")
		return normalized_name

	def validate_email(self, value):
		normalized_email = value.lower()
		if not re.search("^a[0-9]{8}@tec.mx", normalized_email):
			raise serializers.ValidationError("Must be a valid tec email")
		return normalized_email
		
	def validate(self, data):
		password = data.get('user').get('password')
		if password != data.get('user').get('confirm_password'):
			raise serializers.ValidationError({"password": "passwords do not match"})
		try:
			password_validators.validate_password(password=password)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return data 

class ScheduleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Schedule
		fields = ('period', 'day_week', 'hour')

class SubjectTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubjectTutor
		fields = ('subject',)

class TutorRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)
	schedules = ScheduleSerializer(many=True)
	subjects = SubjectTutorSerializer(many=True)

	class Meta:
		model = Tutor
		fields = ('user', 'registration_number', 'email', 'name', 'completed_hours', 'schedules', 'subjects',)
		read_only_fields = ('completed_hours', 'registration_number')

	def create(self, validated_data):
		registration_number = validated_data['email'][:9]
		unique_identifier = 'tutor' + registration_number 

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_tutor = True
		user.save()
		tutor = Tutor.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], name=validated_data['name'])

		schedules_data = validated_data.pop('schedules')
		for schedule in schedules_data:
			Schedule.objects.create(tutor=tutor, **schedule)

		subjects_data = validated_data.pop('subjects')
		for subject in subjects_data:
			SubjectTutor.objects.create(tutor=tutor, **subject)

		return tutor

	def validate_name(self, value):
		normalized_name = value.strip()
		if not re.search("^[a-zA-Zñá-úÁ-Úü]([.](?![.])|[ ](?![ .])|[a-zA-Zñá-úÁ-Úü])*$", normalized_name):
			raise serializers.ValidationError("Name must be valid")
		return normalized_name

	def validate_email(self, value):
		normalized_email = value.lower()
		if not re.search("^a[0-9]{8}@tec.mx", normalized_email):
			raise serializers.ValidationError("Must be a valid tec email")
		return normalized_email

	def validate_schedules(self, value):
		# MIN_SCHEDULES = 5
		# if len(value) >= MIN_SCHEDULES:
		# 	raise serializers.ValidationError(f"The quantity of schedules must greater or equal to ${MIN_SCHEDULES}.")

		PERIOD_CHOICES = [0, 1, 2]
		DAY_WEEK_CHOICES = [0, 1, 2, 3, 4]
		HOUR_CHOICES = [x for x in range(7, 18)]  #[7, 17]
		for schedule in value:
			if schedule['period'] not in PERIOD_CHOICES:
				raise serializers.ValidationError({"Choice of period is incorrect"})
			if schedule['day_week'] not in DAY_WEEK_CHOICES:
				raise serializers.ValidationError({"Choice of day_week is incorrect"})
			if schedule['hour'] not in HOUR_CHOICES:
				raise serializers.ValidationError({"Choice of hour is incorrect"})
		return value

	def validate_subjects(self, value):
		# MIN_SUBJECTS = 10
		# if len(value) >= MIN_SUBJECTS:
		# 	raise serializers.ValidationError(f"The quantity of subjects must be greater or equal to ${MIN_SUBJECTS}.")
		return value

	def validate(self, data):
		password = data.get('user').get('password')
		if password != data.get('user').get('confirm_password'):
			raise serializers.ValidationError({"password": "passwords do not match"})
		try:
			password_validators.validate_password(password=password)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return data 


class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ('code', 'name', 'semester')

