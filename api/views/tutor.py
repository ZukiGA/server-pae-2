from rest_framework import viewsets
from api.models import  Tutor, Subject

from api.serializers import TutorRegisterSerializer, SubjectSerializer

class TutorViewSet(viewsets.ModelViewSet):
	serializer_class = TutorRegisterSerializer
	queryset = Tutor.objects.all()

class SubjectViewSet(viewsets.ModelViewSet):
	serializer_class = SubjectSerializer
	queryset = Subject.objects.all()