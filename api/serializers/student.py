from rest_framework import serializers
from django.core import exceptions
from api.models import User, Student
from django.core.mail import send_mail
import django.contrib.auth.password_validation as password_validators 
from . import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from api.constants import NAME_RE, EMAIL_RE, MAJOR_RE

import re
import datetime
import environ

env = environ.Env()
environ.Env.read_env()

class StudentRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)

	class Meta:
		model = Student 
		fields = ('user', 'registration_number', 'email', 'name', 'major', 'is_active')
		read_only_fields = ('registration_number', 'is_active')

	def create(self, validated_data):
		registration_number = validated_data['email'][:9]
		unique_identifier = 'student' + registration_number

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_student = True
		user.save()
		student = Student.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], major=validated_data['major'], name=validated_data['name'])

		#create a token for activating the account
		token = RefreshToken.for_user(user)
		token.set_exp(lifetime=datetime.timedelta(days=10))
		access_token = token.access_token
		print("token", access_token)
		relative_link = "activate-account/?" + "token=" + str(access_token)
		url = env('FRONTEND_URL') + relative_link
		# send_mail("Activa tu cuenta", "Activar cuenta", None, [validated_data["email"]], html_message=f'<a href="{url}">Activar cuenta</a>')
		send_mail("Activa tu cuenta", "Activar cuenta", None, ["a01731065@tec.mx"], html_message=f'<a href="{url}">Activar cuenta</a>')

		return student 

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
		
	def validate(self, data):
		password = data.get('user').get('password')
		if password != data.get('user').get('confirm_password'):
			raise serializers.ValidationError({"password": "passwords do not match"})
		try:
			password_validators.validate_password(password=password)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return data 