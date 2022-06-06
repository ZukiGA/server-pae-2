from rest_framework import viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from api.models import Tutoring
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.serializers import TutoringSerializer
from api.serializers.tutoring import ChangeTutoringLocationSerializer

class TutoringViewSet(viewsets.ModelViewSet):
	serializer_class = TutoringSerializer
	queryset = Tutoring.objects.all()
	permission_classes = (IsAuthenticatedOrReadOnly,)
	filter_fields = ('status',)

class ChangeTutoringLocation(GenericAPIView, UpdateModelMixin):
	serializer_class = ChangeTutoringLocationSerializer()
	queryset = Tutoring.objects.all()

	def put(self, request):
		return self.partial_update(request)