from rest_framework import serializers
from django.core import exceptions
from api.models import User, Student
import django.contrib.auth.password_validation as password_validators 
from . import UserSerializer
from api.constants import NAME_RE, EMAIL_RE

import re

class StudentRegisterSerializer(serializers.ModelSerializer):
	user = UserSerializer(required=True)

	class Meta:
		model = Student 
		fields = ('user', 'registration_number', 'email', 'name')
		read_only_fields = ('registration_number',)

	def create(self, validated_data):
		registration_number = validated_data['email'][:9]
		unique_identifier = 'student' + registration_number

		user = User.objects.create_user(unique_identifier, validated_data['user']['password'])
		user.is_student = True
		user.save()
		student = Student.objects.create(user=user, registration_number = registration_number, email=validated_data['email'], name=validated_data['name'])
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
		
	def validate(self, data):
		password = data.get('user').get('password')
		if password != data.get('user').get('confirm_password'):
			raise serializers.ValidationError({"password": "passwords do not match"})
		try:
			password_validators.validate_password(password=password)
		except exceptions.ValidationError as e:
			raise serializers.ValidationError({"password": list(e)})
		return data 