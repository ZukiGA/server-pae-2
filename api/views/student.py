from rest_framework import viewsets
from api.models import Student 

from api.serializers import StudentRegisterSerializer

class StudentViewSet(viewsets.ModelViewSet):
	serializer_class = StudentRegisterSerializer
	queryset = Student.objects.all()