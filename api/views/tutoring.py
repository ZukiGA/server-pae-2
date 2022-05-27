from rest_framework import viewsets
from rest_framework.views import APIView
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Schedule, Tutor
from api.serializers import TutoringSerializer, ParamsAvailableTutoringSerializer, AvailableTutoringSerializer, AvailableTutoring

import datetime

# find tutors with subject X
# find schedule of such tutors X
# filter after date


class AvailableTutorings(APIView):
	serializer_class = ParamsAvailableTutoringSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			subject = serializer.validated_data.get("subject")
			date = serializer.validated_data.get("date")
			#find tutors with that subject
			tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject)
			# print(tutors_with_subject)
			#retrieve schedules
			schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject)
			# print(schedules_tutors)
			#TODO: made function for the 3 periods
			#TODO: change hard-coded dates to dates of a period
			initial_date, final_date = datetime.date(2022, 5, 16), datetime.date(2022, 6, 17) #hard-coded dates
			initial_date = max(date.today()+datetime.timedelta(days=1), initial_date)
			delta = final_date - initial_date
			third_period = [initial_date + datetime.timedelta(days=i) for i in range(delta.days + 1)] 
			days_by_week = {}
			for i in range(1, 6):
				days_by_week[i] = []
			for date_in_period in third_period:
				if date_in_period.weekday() >= 1 and date_in_period.weekday() <= 5:
					days_by_week[date_in_period.weekday()].append(date_in_period)	



			available_tutorings = []
			for schedule in schedules_tutors:
				for date_in_period in days_by_week[schedule.day_week]:
				#TODO: validate tutor and student are the same person
					available_tutorings.append(AvailableTutoring(date=date_in_period, hour=schedule.hour, period=schedule.period, tutor=schedule.tutor))						

			available_tutorings.sort(key=lambda x: (x.date, x.hour))

			return Response(AvailableTutoringSerializer(available_tutorings, many=True).data)


class TutoringViewSet(viewsets.ModelViewSet):
	serializer_class = TutoringSerializer
	queryset = Tutoring.objects.all()
	permission_classes = (IsAuthenticated,)



