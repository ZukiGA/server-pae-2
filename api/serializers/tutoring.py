from rest_framework import serializers
from api.models import Tutoring, Schedule

from api.constants import HOUR_CHOICES 

from django.utils.encoding import smart_bytes
from django.utils.http import urlsafe_base64_encode

class ParamsAvailableTutoringSerializer(serializers.Serializer):
	subject = serializers.CharField()
	initial_date_serializer = serializers.DateField()
	final_date_serializer = serializers.DateField()

class AvailableTutoring(object):
	def __init__(self, hour, period, tutor):
		self.hour = hour
		self.period = period
		#encode registration number of tutor to avoid identification
		# self.tutor = urlsafe_base64_encode(smart_bytes(tutor.registration_number))
		self.tutor = tutor.registration_number

class AvailableTutoringSerializer(serializers.Serializer):
		hour = serializers.IntegerField()
		period = serializers.IntegerField()
		tutor = serializers.CharField()

class AvailableTutoringSerializerList(serializers.Serializer):
	date = serializers.DateField()
	tutorings = AvailableTutoringSerializer(many=True)

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