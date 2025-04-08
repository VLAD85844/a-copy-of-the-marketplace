from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
import json
from .models import Profile
from .serializers import ProfileSerializer


class SignInView(APIView):
    def post(self, request):
        """Авторизация пользователя"""
        serialized_data = list(request.POST.keys())[0]
        user_data = json.loads(serialized_data)
        username = user_data.get("username")
        password = user_data.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(APIView):
    def post(self, request):
        """Регистрация пользователя"""
        serialized_data = list(request.data.keys())[0]
        user_data = json.loads(serialized_data)
        username = user_data.get("username")
        password = user_data.get("password")
        name = user_data.get("name")

        try:
            user = User.objects.create_user(username=username, password=password)
            profile = Profile.objects.create(user=user, fullName=name)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
            return Response(status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Возвращает профиль пользователя"""
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        """Обновляет профиль пользователя"""
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def signUp(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            username = body.get('username')
            email = body.get('email')
            password = body.get('password')
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            profile = Profile.objects.create(user=user, fullName=username)
            profile.save()

            return JsonResponse({"message": "User and profile created successfully"}, status=200)

        except Exception as e:
            print(f"Error during sign-up: {e}")
            return JsonResponse({"error": "Registration failed"}, status=500)

def signOut(request):
    """Разлогинивание пользователя"""
    logout(request)
    return Response(status=status.HTTP_200_OK)