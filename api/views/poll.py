from rest_framework import viewsets, filters
from rest_framework.views import APIView
from django.db.models import Count
from api.models import Question, Poll, QuestionPoll
from rest_framework.response import Response

from api.serializers import QuestionSerializer, PollSerializer
from api.serializers.poll import PollResultsSerializer

class QuestionViewSet(viewsets.ModelViewSet):
	serializer_class = QuestionSerializer
	queryset = Question.objects.all().order_by('id')

class PollViewSet(viewsets.ModelViewSet):
	serializer_class = PollSerializer
	queryset = Poll.objects.all()

def auxSort(dict):
	return dict['result']

class PollResults(APIView):
	def get(self, request):
		questions = Question.objects.filter()
		results_questions = []
		for question in questions:
			results = QuestionPoll.objects.filter(question=question).values('result').annotate(total = Count('result'))
			results_list = list(results)
			missing_results = [i for i in range(1, 5) if i not in [dict['result'] for dict in results_list]]
			for m in missing_results:
				results_list.append({'result': m, 'total': 0})
			results_list.sort(key=auxSort)
			results_questions.append({"question": question, "results": results_list})
		
		return Response((PollResultsSerializer(results_questions, many=True)).data)