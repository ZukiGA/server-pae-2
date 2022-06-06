from django.db import models
from .user import User

class Student(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	email = models.EmailField(max_length=255, unique=True)
	name = models.CharField(max_length=255)
	registration_number = models.TextField(max_length=9, primary_key=True)
	major = models.CharField(max_length=4)
	is_active = models.BooleanField(default=False)

	def delete(self, *args, **kwargs):
		super().delete(*args, **kwargs)
		if self.user:
			self.user.delete()