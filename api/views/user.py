from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from api.models import Student, Tutor, User
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import smart_bytes, smart_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from api.serializers import LogoutSerializer, ResetPasswordEmailSerializer, ResetPasswordTokenSerializer, ChangePasswordSerializer

import environ

env = environ.Env()
environ.Env.read_env()

class Login(ObtainAuthToken):
	def post(self, request):
		login_serializer = self.serializer_class(data=request.data, context = {'request': request})
		if login_serializer.is_valid():
			user = login_serializer.validated_data['user']
			token, _ = Token.objects.get_or_create(user = user)
			return Response({
				'token': token.key,
				'user': user.role_account.name,
				'message': "Successful login" 
			}, status=status.HTTP_201_CREATED)
		return Response({'message': 'Username or password is incorrect'}, status=status.HTTP_401_UNAUTHORIZED)

class Logout(APIView):
	serializer_class = LogoutSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			if not Token.objects.filter(key = token).exists():
				return Response({"token": "No such token"}, status=status.HTTP_400_BAD_REQUEST)
			token = Token.objects.get(key = token)
			token.delete()
			return Response({"token": "Token successfully deleted"}, status=status.HTTP_200_OK)

class ResetPasswordEmail(APIView):
	serializer_class = ResetPasswordEmailSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			email = serializer.validated_data.get('email')
			user_type = serializer.validated_data.get('user_type')
			user = None
			if user_type == 0: #Student
				if not Student.objects.filter(email=email).exists():
					return Response({"email": 'There is no student with such email'}, status=status.HTTP_400_BAD_REQUEST)
				user = Student.objects.get(email=email).user
			elif user_type == 1: #Tutor
				if not Tutor.objects.filter(email=email).exists():
					return Response({"email": 'There is no tutor with such email'}, status=status.HTTP_400_BAD_REQUEST)
				user = Tutor.objects.get(email=email).user
			else:
				return Response({"user_type": "No such user type"}, status=status.HTTP_400_BAD_REQUEST)
		# 	#TODO Admin

			ui64 = urlsafe_base64_encode(smart_bytes(user.unique_identifier))
			token = PasswordResetTokenGenerator().make_token(user)
			relative_link = "reset-password/?" + "uid=" + ui64 + "&token=" + token
			url = env('FRONTEND_URL') + relative_link
			# print(token, ui64, url)
			send_mail('Por favor cambia tu password', "Cambiar password", None, [email], html_message=f'<a href="{url}">Cambiar password</a>')
			return Response({"message": "An email has been sent"}, status=status.HTTP_201_CREATED)


class ResetPasswordToken(APIView):
	serializer_class = ResetPasswordTokenSerializer
	def post(self, request):
		serializer = self.serializer_class(data=request.data)
		if serializer.is_valid(raise_exception=True):
			token = serializer.validated_data.get('token')
			ui64 = serializer.validated_data.get('ui64')
			new_password = serializer.validated_data.get('new_password')
			ui = smart_str(urlsafe_base64_decode(ui64))
			print(ui)
			if not User.objects.filter(unique_identifier=ui).exists():
				return Response({"user": "No such user"}, status=status.HTTP_400_BAD_REQUEST)
			user = User.objects.get(unique_identifier=ui)
			if not PasswordResetTokenGenerator().check_token(user, token):
				return Response({"token": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)
			if user.check_password(new_password):
				return Response({"new_password": "You are using the same password"}, status=status.HTTP_400_BAD_REQUEST)
			user.set_password(new_password)
			user.save()
			return Response({"message": "Password was resetted successfully"}, status=status.HTTP_200_OK)

class ChangePassword(APIView):
	permission_classes = (IsAuthenticated,)
	serializer_class = ChangePasswordSerializer
	def patch(self, request):
		serializer = self.serializer_class(data=request.data, context = {'request': request})
		if serializer.is_valid(raise_exception=True):
			user = serializer.context['request'].user
			password = serializer.validated_data.get('password')
			new_password = serializer.validated_data.get('new_password')
			if user.check_password(new_password):
				return Response({"new_password": "the new password is the same as the old password"}, status=status.HTTP_400_BAD_REQUEST)
			if not user.check_password(password):
				return Response({"password": "the password provided is incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
			user.set_password(new_password)
			user.save()
			return  Response({"message": "password changed successfully"}, status=status.HTTP_200_OK)
	