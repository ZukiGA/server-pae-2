from rest_framework import serializers
from django.core import exceptions
from api.models import Schedule, SubjectTutor, User, Tutor, Subject
import django.contrib.auth.password_validation as password_validators
from .user import UserSerializer
from api.constants import HOUR_CHOICES, PERIOD_CHOICES, DAY_WEEK_CHOICES, NAME_RE, EMAIL_RE

import re

class SubjectTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubjectTutor
		fields = ('subject',)

class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ('code', 'name', 'semester')

class ScheduleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Schedule
		fields = ('period', 'day_week', 'hour')

class TutorRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)
	schedules = ScheduleSerializer(many=True)
	subjects = SubjectTutorSerializer(many=True)

	class Meta:
		model = Tutor
		fields = ('user', 'registration_number', 'email', 'name', 'completed_hours', 'schedules', 'subjects', 'is_active')
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
		if not re.search(NAME_RE, normalized_name):
			raise serializers.ValidationError("Name must be valid")
		return normalized_name

	def validate_email(self, value):
		normalized_email = value.lower()
		if not re.search(EMAIL_RE, normalized_email):
			raise serializers.ValidationError("Must be a valid tec email")
		return normalized_email

	def validate_schedules(self, value):
		# MIN_SCHEDULES = 5
		# if len(value) >= MIN_SCHEDULES:
		# 	raise serializers.ValidationError(f"The quantity of schedules must greater or equal to ${MIN_SCHEDULES}.")

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

