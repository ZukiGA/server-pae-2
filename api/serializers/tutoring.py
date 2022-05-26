from rest_framework import serializers
from api.models import Tutoring, Schedule

from api.constants import HOUR_CHOICES 

class ParamsTutoringSerializer(serializers.Serializer):
	subject = serializers.CharField()
	# date = serializers.DateField()

class AvailableTutoring(serializers.ModelSerializer):
	class Meta:
		model = Schedule
		fields = ('__all__')
		depth = 1

class TutoringSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutoring
		fields = ('__all__')
		read_only_fields = ('student', 'status')

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