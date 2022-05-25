from django.db import models
from .tutor import Tutor, Subject
from .tutee import Tutee

def upload_to(instance, filename):
	return 'tutoring/{filename}'.format(filename=filename)

class Tutoring(models.Model):
	class StatusTutoring(models.TextChoices):
		PENDING = 'PE', 'Pending'
		APPROVED = 'AP', 'Approved'
		COMPLETED = 'CO', 'Completed'

	tutor = models.ForeignKey(Tutor, null=True, on_delete=models.SET_NULL)
	tutee = models.ForeignKey(Tutee, null=True, on_delete=models.SET_NULL)
	subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
	date = models.DateField()
	hour = models.PositiveIntegerField()
	status = models.CharField(max_length=2, choices=StatusTutoring.choices, default=StatusTutoring.PENDING)
	is_online = models.BooleanField()
	topic = models.CharField(max_length=255)
	doubt = models.TextField(null=True)
	file = models.ImageField('images', upload_to=upload_to, null=True)