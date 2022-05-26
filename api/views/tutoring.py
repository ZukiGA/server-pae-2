from rest_framework import viewsets
from rest_framework.views import APIView
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Schedule, Tutor

from api.serializers import TutoringSerializer, ParamsTutoringSerializer, AvailableTutoring

# find tutors with subject X
# find schedule of such tutors X
# filter after date


class AvailableTutorings(APIView):
	serializer_class = ParamsTutoringSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			subject = serializer.validated_data.get("subject")
			date = serializer.validated_data.get("date")
			#find tutors with that subject
			tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject)
			print(tutors_with_subject)
			#retrieve schedules
			schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject)
			print(schedules_tutors)

			return Response(AvailableTutoring(schedules_tutors, many=True).data)


class TutoringViewSet(viewsets.ModelViewSet):
	serializer_class = TutoringSerializer
	queryset = Tutoring.objects.all()
	permission_classes = (IsAuthenticated,)



