from rest_framework import viewsets
from rest_framework.views import APIView
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from api.models import Schedule, Tutor
from api.serializers import TutoringSerializer, ParamsAvailableTutoringSerializer, AvailableTutoringSerializerList, AvailableTutoring

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
			initial_date_serializer = serializer.validated_data.get("initial_date_serializer")
			final_date_serializer = serializer.validated_data.get("final_date_serializer")

			#find tutors with that subject
			tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject).order_by("completed_hours").reverse()
			#retrieve schedules
			schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject)
			#TODO: made function for the 3 periods
			#TODO: change hard-coded dates to dates of a period
			initial_date, final_date = datetime.date(2022, 5, 16), datetime.date(2022, 6, 17) #hard-coded dates
			initial_date = max(initial_date_serializer, initial_date)
			final_date = min(final_date_serializer, final_date)
			delta = final_date - initial_date
			third_period = [initial_date + datetime.timedelta(days=i) for i in range(delta.days + 1)] 
			days_by_week = {}
			available_tutorings = {}
			for i in range(1, 6):
				days_by_week[i] = []
			for date_in_period in third_period:
				if date_in_period.weekday() >= 1 and date_in_period.weekday() <= 5:
					available_tutorings[date_in_period] = []
					days_by_week[date_in_period.weekday()].append(date_in_period)	



			for schedule in schedules_tutors:
				for date_in_period in days_by_week[schedule.day_week]:
					available_tutorings[date_in_period].append(AvailableTutoring(hour=schedule.hour, period=schedule.period, tutor=schedule.tutor))
					#TODO: validate tutor and student are not the same person

			tutorings_with_same_tutors = Tutoring.objects.filter(tutor__in=tutors_with_subject)
			for tutoring in tutorings_with_same_tutors:
				print(tutoring.date)
				if tutoring.date in available_tutorings:
					available_tutorings[tutoring.date] = list(filter(lambda x: x.hour != tutoring.hour or x.tutor != tutoring.tutor.registration_number, available_tutorings[tutoring.date]))


			list_available_tutorings = []
			for available_tutoring in available_tutorings.items():
				list_available_tutorings.append({"date": available_tutoring[0], "tutorings": available_tutoring[1]})

			return Response(AvailableTutoringSerializerList(list_available_tutorings, many=True).data)


class TutoringViewSet(viewsets.ModelViewSet):
	serializer_class = TutoringSerializer
	queryset = Tutoring.objects.all()
	permission_classes = (IsAuthenticated,)



