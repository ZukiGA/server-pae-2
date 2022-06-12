from pyexpat import model
from rest_framework import serializers
from django.core import exceptions
from django.core.mail import send_mail
from api.models import Schedule, SubjectTutor, User, Tutor, Subject
import django.contrib.auth.password_validation as password_validators
from .user import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.constants import HOUR_CHOICES, PERIOD_CHOICES, DAY_WEEK_CHOICES, NAME_RE, EMAIL_RE, MAJOR_RE

import re
import datetime
import environ

env = environ.Env()
environ.Env.read_env()

class SubjectTutorSerializer(serializers.ModelSerializer):
	class Meta:
		model = SubjectTutor
		fields = ('subject', 'tutor')
		
class SubjectTutorSerializerRegister(serializers.ModelSerializer):
	class Meta:
		model = SubjectTutor
		fields = ('subject',)

class SubjectSerializer(serializers.ModelSerializer):
	class Meta:
		model = Subject
		fields = ('code', 'name', 'semester')
	
	def validate_code(self, value):
		if len(value) < 7:
			raise serializers.ValidationError("code must be greater than 7 ")
		if len(value) > 8:
			raise serializers.ValidationError("code must be less than 8")
		return value

class ScheduleSerializer(serializers.ModelSerializer):
	class Meta:
		model = Schedule
		fields = ('period', 'day_week', 'hour')

class TutorRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)
	schedules = ScheduleSerializer(many=True)
	subjects = SubjectTutorSerializerRegister(many=True)

	class Meta:
		model = Tutor
		fields = ('user', 'registration_number', 'email', 'name', 'major', 'completed_hours', 'schedules', 'subjects', 'is_active', 'is_accepted')
		read_only_fields = ('completed_hours', 'registration_number', 'is_active', 'is_accepted',)

	def create(self, validated_data):
		registration_number = validated_data['email'][:9]
		unique_identifier = 'tutor' + registration_number 
		
		#create a user for that tutor
		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_tutor = True
		user.save()

		#create the tutor
		tutor = Tutor.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], name=validated_data['name'], major=validated_data['major'])

		#create schedules for that user
		schedules_data = validated_data.pop('schedules')
		for schedule in schedules_data:
			Schedule.objects.create(tutor=tutor, **schedule)

		#create subjects for that user
		subjects_data = validated_data.pop('subjects')
		for subject in subjects_data:
			SubjectTutor.objects.create(tutor=tutor, **subject)

		#create a token for activating the account
		token = RefreshToken.for_user(user)
		token.set_exp(lifetime=datetime.timedelta(days=10))
		access_token = token.access_token
		print("token", access_token)
		relative_link = "activate-account/?" + "token=" + str(access_token)
		url = env('FRONTEND_URL') + relative_link
		send_mail("Activa tu cuenta", "Activar cuenta", None, [validated_data["email"]], html_message=f'<a href="{url}">Activar cuenta</a>')

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

	def validate_major(self, value):
		normalized_major = value.upper()
		if not re.search(MAJOR_RE, normalized_major):
			raise serializers.ValidationError("Must contain only letters")
		if len(normalized_major) < 2:
			raise serializers.ValidationError("Must be longer than 2 letters")
		return normalized_major

	def validate_schedules(self, value):
		MIN_SCHEDULES = 5
		if len(value) >= MIN_SCHEDULES:
			raise serializers.ValidationError(f"The quantity of schedules must greater or equal to ${MIN_SCHEDULES}.")

		for schedule in value:
			if schedule['period'] not in PERIOD_CHOICES:
				raise serializers.ValidationError({"Choice of period is incorrect"})
			if schedule['day_week'] not in DAY_WEEK_CHOICES:
				raise serializers.ValidationError({"Choice of day_week is incorrect"})
			if schedule['hour'] not in HOUR_CHOICES:
				raise serializers.ValidationError({"Choice of hour is incorrect"})
		return value

	def validate_subjects(self, value):
		MIN_SUBJECTS = 1
		if len(value) >= MIN_SUBJECTS:
			raise serializers.ValidationError(f"The quantity of subjects must be greater or equal to ${MIN_SUBJECTS}.")
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

class TutorIsAcceptedSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ('is_accepted',)

class ModifyScheduleSerializer(serializers.Serializer):
	schedules = ScheduleSerializer(many=True)
	tutor = serializers.PrimaryKeyRelatedField(queryset=Tutor.objects.all())

class VerifyEmailSerializer(serializers.Serializer):
	token = serializers.CharField()

