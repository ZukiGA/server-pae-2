from rest_framework import serializers
from django.core import exceptions
from api.models import Schedule, SubjectTutor, Tutoring, User, Tutee, Tutor, Subject
import django.contrib.auth.password_validation as password_validators 

HOUR_CHOICES = [x for x in range(7, 18)]  #[7, 17]

class TutoringSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ('__all__')
		read_only_fields = ('tutee', 'status')

	def create(self, validated_data):
		tutee = self.context['request'].user.role_account
		return Tutoring.objects.create(tutee = tutee, **validated_data)

	def validate_tutor(self, value):
		if value is None:
			raise serializers.ValidationError({"tutor": "tutor cannot be null"})
		return value

	def validate_subject(self, value):
		if value is None:
			raise serializers.ValidationError({"subject": "subjct cannot be null"})
		return value
	
	def validate_hour(self, value):	
		if value not in HOUR_CHOICES:
			raise serializers.ValidationError({"hour": "hour must be between 7 and 17"})
		return value

	def validate(self, data):
		if data["doubt"] is None and data["file"] is None:
			raise serializers.ValidationError({"doubt": "there must a doubt or a file"})
		return data