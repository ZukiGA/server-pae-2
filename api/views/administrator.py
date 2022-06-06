from rest_framework import viewsets
from api.models import Administrator 

from api.serializers import AdministratorSerializer

class AdministratorViewSet(viewsets.ModelViewSet):
	serializer_class = AdministratorSerializer
	queryset = Administrator.objects.all()