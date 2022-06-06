from rest_framework import serializers
from api.models import Question, QuestionPoll, Poll, Tutor

class TutorPollSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tutor
		fields = ('name', 'registration_number')

class QuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = ('__all__')

class QuestionPollSerializer(serializers.ModelSerializer):
	question = QuestionSerializer(read_only=True)
	question_id = serializers.PrimaryKeyRelatedField(write_only=True, source='question', queryset=Question.objects.all())

	class Meta:
		model = QuestionPoll
		fields = ('question_id', 'question', 'result',)
		depth = 1


class PollSerializer(serializers.ModelSerializer):
	question_polls = QuestionPollSerializer(many=True)
	tutor = TutorPollSerializer(read_only=True)

	class Meta:
		model = Poll
		fields = ('tutoring', 'comment', 'question_polls', 'tutor')

	def create(self, validated_data):
		question_poll_data = validated_data.pop('question_polls')
		poll = Poll.objects.create(tutoring=validated_data['tutoring'], comment=validated_data['comment'])
		for question_poll in question_poll_data:
			QuestionPoll.objects.create(poll=poll, **question_poll)
		return poll

	def validate_question_polls(self, value):
		num_questions = Question.objects.count()
		if num_questions != len(value):
			raise serializers.ValidationError("Received incorrect number of questions")
		visited_questions = set()
		for x in value:
			pk_question = x['question'].pk
			if pk_question in visited_questions:
				raise serializers.ValidationError("Repeated question")
			visited_questions.add(pk_question)	
		return value


