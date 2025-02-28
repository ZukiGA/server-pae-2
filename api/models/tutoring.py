from django.db import models
from .tutor import Tutor, Subject
from .student import Student 

from api.utils import upload_to

class Tutoring(models.Model):
	class StatusTutoring(models.TextChoices):
		PENDING = 'PE', 'Pending'
		APPROVED = 'AP', 'Approved'
		COMPLETED = 'CO', 'Completed'

	tutor = models.ForeignKey(Tutor, null=True, on_delete=models.SET_NULL)
	student = models.ForeignKey(Student, null=True, on_delete=models.SET_NULL)
	subject = models.ForeignKey(Subject, null=True, on_delete=models.SET_NULL)
	date = models.DateField()
	hour = models.PositiveIntegerField()
	status = models.CharField(max_length=2, choices=StatusTutoring.choices, default=StatusTutoring.PENDING)
	is_online = models.BooleanField()
	topic = models.CharField(max_length=255)
	doubt = models.TextField(null=True)
	file = models.ImageField('images', upload_to=upload_to, null=True)