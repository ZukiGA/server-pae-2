from django.urls import reverse
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from .models import Tutee, Tutor, User, Subject

from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
import environ

from . import serializers

env = environ.Env()
environ.Env.read_env()

class TuteeViewSet(viewsets.ModelViewSet):
	serializer_class = serializers.TuteeRegisterSerializer
	queryset = Tutee.objects.all()

class TutorViewSet(viewsets.ModelViewSet):
	serializer_class = serializers.TutorRegisterSerializer
	queryset = Tutor.objects.all()

class SubjectViewSet(viewsets.ModelViewSet):
	serializer_class = serializers.SubjectSerializer
	queryset = Subject.objects.all()

class LoginTutee(ObtainAuthToken):
	def post(self, request):
		login_serializer = self.serializer_class(data=request.data, context = {'request': request})
		if login_serializer.is_valid():
			user = login_serializer.validated_data['user']
			token, created = Token.objects.get_or_create(user = user)
			return Response({
				'token': token.key,
				'user': str(user),
				'message': "Successful login" 
			}, status=status.HTTP_201_CREATED)
		else:
			return Response({'message': 'Username or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)		 
class ResetPasswordEmail(APIView):
	serializer_class = serializers.ResetPasswordEmailSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			email = serializer.validated_data.get('email')
			user_type = serializer.validated_data.get('user_type')
			user = None
			if user_type == 0: #Student
				if Tutee.objects.filter(email=email).exists():
					user = Tutee.objects.get(email=email).user
				else: 
					return Response({"email": 'There is no student with such email'}, status=status.HTTP_400_BAD_REQUEST)
			elif user_type == 1: #Tutor
				if Tutor.objects.filter(email=email).exists():
					user = Tutor.objects.get(email=email).user
				else: 
					return Response({"email": 'There is no tutor with such email'}, status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response({"user_type": "No such user type"}, status=status.HTTP_400_BAD_REQUEST)
		# 	#TODO Admin
		ui64 = urlsafe_base64_encode(smart_bytes(user.unique_identifier))
		token = PasswordResetTokenGenerator().make_token(user)
		relative_link = "change-password/?" + "uid=" + ui64 + "&token=" + token
		url = env('FRONTEND_URL') + relative_link
		print(token, ui64, url)
		# send_mail('Por favor cambia tu password', "Cambiar password", None, [email], html_message=f'<a href="{url}">Cambiar password</a>')
		return Response({"message": "An email has been sent"}, status=status.HTTP_201_CREATED)


class ResetPasswordToken(APIView):
	serializer_class = serializers.ResetPasswordTokenSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			ui64 = serializer.validated_data.get('ui64')
			new_password = serializer.validated_data.get('new_password')
			ui = smart_str(urlsafe_base64_decode(ui64))
			print(ui)
			if User.objects.filter(unique_identifier=ui).exists():
				user = User.objects.get(unique_identifier=ui)
				if PasswordResetTokenGenerator().check_token(user, token):
					if user.check_password(new_password):
						return Response({"new_password": "Your are using the same password"}, status=status.HTTP_400_BAD_REQUEST)
					user.set_password(new_password)
					user.save()
					return Response({"message": "Password was resetted successfully"})
				else:
					return Response({"token": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
			else:
				return Response({"user": "No such user"}, status=status.HTTP_400_BAD_REQUEST)


class LoginTutor(APIView):
	serializer_class = serializers.LoginSerializer
	def post(self, request):
		registration_number = request.data['registration_number']
		password = request.data['password']

		tutor = Tutor.objects.filter(registration_number=registration_number).exists()
		if tutor:
			unique_identifier = "tutor" + registration_number
			user = User.objects.get(unique_identifier=unique_identifier)
			if user.check_password(password):
				return Response({"user": "logged in"}, status=status.HTTP_200_OK)
			return Response({"Error": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
		tutor = Tutor.objects.filter(email=registration_number).exists()
		if tutor:
			unique_identifier = "tutor" + registration_number
			user = User.objects.get(unique_identifier=unique_identifier)
			if user.check_password(password):
				return Response({"user": "logged in"}, status=status.HTTP_200_OK)
			return Response({"Error": "wrong password"}, status=status.HTTP_401_UNAUTHORIZED)
		return Response({"Error": "wrong user"}, status=status.HTTP_401_UNAUTHORIZED)