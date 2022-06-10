from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnUser(BasePermission):
	def has_object_permission(self, request, view, obj):
		request.user == obj

class IsAdminOrStudent(BasePermission):
	def has_permission(self, request, view):
		return request.user.is_administrator or request.user.is_student

class IsAdmin(BasePermission):
	def has_permission(self, request, view):
		return request.user.is_administrator

class TutoringViewsetPermission(BasePermission):
	def has_permission(self, request, view):
		print(request.user.is_authenticated)
		# if request.user.is_authenticated:
			
		if request.method in SAFE_METHODS:
			return True
		return request.user.is_administrator or request.user.is_student
# class IsAdminOrReadOnly(BasePermission):
