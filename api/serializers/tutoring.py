from rest_framework import serializers
from api.models import Tutoring

from api.constants import HOUR_CHOICES 

class TutoringSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ('__all__')
		read_only_fields = ('student', 'status')
		depth = 1

	def create(self, validated_data):
		student = self.context['request'].user.role_account
		return Tutoring.objects.create(student = student, **validated_data)

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

class ChangeTutoringLocationSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ()