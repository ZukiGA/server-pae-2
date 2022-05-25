from rest_framework import serializers
from django.core import exceptions
from api.models import Schedule, SubjectTutor, Tutoring, User, Tutee, Tutor, Subject
import django.contrib.auth.password_validation as password_validators 
from . import UserSerializer

import re

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