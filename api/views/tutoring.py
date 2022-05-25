from rest_framework import viewsets
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticated 

from api.serializers import TutoringSerializer

class TutoringViewSet(viewsets.ModelViewSet):
	serializer_class = TutoringSerializer
	queryset = Tutoring.objects.all()
	permission_classes = (IsAuthenticated,)