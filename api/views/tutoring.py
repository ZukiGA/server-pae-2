import sched
from rest_framework import viewsets
from rest_framework.views import APIView
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from api.models import Schedule, Tutor, Period, Tutoring
from api.serializers import TutoringSerializer, ParamsAvailableTutoringSerializer, AvailableTutoringSerializerList, AvailableTutoring
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin

from api.serializers.tutoring import ChangeTutoringLocationSerializer

import datetime

# find tutors with subject X
# find schedule of such tutors X
# filter after date

#constants for lookup in Period table
START_DATE_FIELDS = ["beginning_first_period", "beginning_second_period", "beginning_third_period"]
END_DATE_FIELDS = ["ending_first_period", "ending_second_period", "ending_third_period"]


class AvailableTutorings(APIView):
    serializer_class = ParamsAvailableTutoringSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            subject = serializer.validated_data.get("subject")
            initial_date_serializer = serializer.validated_data.get("initial_date_serializer")
            final_date_serializer = serializer.validated_data.get("final_date_serializer")

            # find tutors with that subject
            tutors_with_subject = Tutor.objects.filter(subjecttutor__subject=subject).order_by("completed_hours").reverse()
            # retrieve schedules
            schedules_tutors = Schedule.objects.filter(tutor__in=tutors_with_subject)
            #it gets the start and end dates of the period
            period = Period.objects.filter().first()
            list_available_tutorings = []

            #it goes for the 3 periods
            for current_period in range(3):
                #it gets the initial and end date for that period
                start_date, end_date = START_DATE_FIELDS[current_period], END_DATE_FIELDS[current_period]
                initial_date, final_date = period.__dict__[start_date], period.__dict__[end_date]
                #checks if period is inside asked dates
                if not (initial_date_serializer > final_date or final_date_serializer < initial_date):
                    #checks if it has to use dates of period or dates asked
                    initial_date = max(initial_date_serializer, initial_date)
                    final_date = min(final_date_serializer, final_date)
                    delta = final_date - initial_date
                    #gets dates in that period
                    current_period_dates = [initial_date + datetime.timedelta(days=current_period) for current_period in range(delta.days + 1)]
                    #split dates by day of the week
                    days_by_week = {}
                    available_tutorings = {}
                    for i in range(0, 6):
                        days_by_week[i] = []
                    for date_in_period in current_period_dates:
                        if date_in_period.weekday() >= 0 and date_in_period.weekday() <= 4:
                            available_tutorings[date_in_period] = []
                            days_by_week[date_in_period.weekday()+1].append(date_in_period)

                    #creates possible tutorings with the schedules and the dates in this period
                    for schedule in schedules_tutors:
                        if schedule.period == current_period+1:
                            for date_in_period in days_by_week[schedule.day_week]:
                                available_tutorings[date_in_period].append(AvailableTutoring(hour=schedule.hour, period=schedule.period, tutor=schedule.tutor, isOnline=True))
                                # TODO: validate tutor and student are not the same person

                    #eliminates if there is already a tutoring at that time and with the same tutor
                    tutorings_with_same_tutors = Tutoring.objects.filter(tutor__in=tutors_with_subject)
                    for tutoring in tutorings_with_same_tutors:
                        if tutoring.date in available_tutorings:
                            available_tutorings[tutoring.date] = list(filter(
                                lambda x: x.hour != tutoring.hour or x.tutor != tutoring.tutor.registration_number, available_tutorings[tutoring.date]))

                    #gives format for returning
                    for available_tutoring in available_tutorings.items():
                        list_available_tutorings.append({"date": available_tutoring[0], "tutorings": available_tutoring[1]})

            return Response(AvailableTutoringSerializerList(list_available_tutorings, many=True).data)


class TutoringViewSet(viewsets.ModelViewSet):
    serializer_class = TutoringSerializer
    queryset = Tutoring.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ('status',)

class ChangeTutoringLocation(GenericAPIView, UpdateModelMixin):
	serializer_class = ChangeTutoringLocationSerializer
	queryset = Tutoring.objects.all()

	def put(self, request, *args, **kwargs):
		return self.partial_update(request, *args, **kwargs)
