from django.db import models
from .tutoring import Tutoring

CHOICES = [(i,i) for i in range(1, 5)]

class Poll(models.Model):
	tutoring = models.OneToOneField(Tutoring, null=True, on_delete=models.CASCADE)
	comment = models.TextField()

	@property
	def question_polls(self):
		return self.questionpoll_set.all()

	@property
	def get_average(self):
		return QuestionPoll.objects.filter(poll = self.pk)

class Question(models.Model):
	body = models.TextField()

class QuestionPoll(models.Model):
	poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
	question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)
	result = models.IntegerField(choices=CHOICES)


