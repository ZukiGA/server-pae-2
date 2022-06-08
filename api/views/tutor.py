from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from api.models import  Tutor, Subject, User, SubjectTutor
from rest_framework.authtoken.models import Token
import jwt

from api.serializers import TutorRegisterSerializer, SubjectSerializer, VerifyEmailSerializer, TutorIsAcceptedSerializer
from api.serializers.tutor import SubjectTutorSerializer
from server.settings import SECRET_KEY

class TutorViewSet(viewsets.ModelViewSet):
	serializer_class = TutorRegisterSerializer
	queryset = Tutor.objects.all()

class TutorIsAccepted(GenericAPIView, UpdateModelMixin):
	serializer_class = TutorIsAcceptedSerializer
	queryset = Tutor.objects.all()

	def put(self, request, *args, **kwargs):
		return self.partial_update(request, *args, **kwargs)

class SubjectViewSet(viewsets.ModelViewSet):
	serializer_class = SubjectSerializer
	queryset = Subject.objects.all()

class SubjectByTutor(APIView):
	def get(self, request, *args, **kwargs):
		tutor = self.kwargs['tutor']
		subject_tutor = SubjectTutor.objects.filter(tutor = tutor)
		subjects = []
		for subject_tutor_object in subject_tutor:
			subjects.append(subject_tutor_object.subject)
		return Response(SubjectSerializer(subjects, many=True).data, status=status.HTTP_200_OK)	

class VerifyEmail(APIView):
	serializer_class = VerifyEmailSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get("token")
			key = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
			print(key)
			user = User.objects.get(unique_identifier=key['user_id'])
			tutor_or_student = user.role_account
			if not tutor_or_student.is_active:
				tutor_or_student.is_active = True
				tutor_or_student.save()
				token, _ = Token.objects.get_or_create(user = user)
				return Response({
					'token': token.key,
					'user': user.role_account.name,
					'message': "Successful login" 
				}, status=status.HTTP_201_CREATED)
			return Response({"token": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)