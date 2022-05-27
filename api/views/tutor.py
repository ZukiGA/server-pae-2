from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from api.models import  Tutor, Subject, User
from rest_framework.authtoken.models import Token
import jwt

from api.serializers import TutorRegisterSerializer, SubjectSerializer, VerifyEmailSerializer
from server.settings import SECRET_KEY

class TutorViewSet(viewsets.ModelViewSet):
	serializer_class = TutorRegisterSerializer
	queryset = Tutor.objects.all()

class SubjectViewSet(viewsets.ModelViewSet):
	serializer_class = SubjectSerializer
	queryset = Subject.objects.all()

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