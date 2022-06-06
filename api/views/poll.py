from rest_framework import viewsets
from api.models import Question, Poll

from api.serializers import QuestionSerializer, PollSerializer

class QuestionViewSet(viewsets.ModelViewSet):
	serializer_class = QuestionSerializer
	queryset = Question.objects.all()

class PollViewSet(viewsets.ModelViewSet):
	serializer_class = PollSerializer
	queryset = Poll.objects.all()