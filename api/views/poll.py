from rest_framework import viewsets
from api.models import Question

from api.serializers import QuestionSerializer

class QuestionViewSet(viewsets.ModelViewSet):
	serializer_class = QuestionSerializer
	queryset = Question.objects.all()