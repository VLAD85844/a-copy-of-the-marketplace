from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
import json
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Avatar
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


class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Обновляет пароль пользователя"""
        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')

        user = request.user

        if not user.check_password(current_password):
            return Response({"error": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Возвращает профиль пользователя"""
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        """Обновляет профиль пользователя"""
        user = request.user
        profile = Profile.objects.get(user=user)

        current_password = request.data.get('currentPassword')
        new_password = request.data.get('newPassword')
        if current_password and new_password:
            if not user.check_password(current_password):
                return Response({"error": "Incorrect current password"}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.save()

        if 'email' in request.data:
            profile.email = request.data['email']
            profile.save()

        profile.fullName = request.data.get('fullName', profile.fullName)
        profile.phone = request.data.get('phone', profile.phone)

        avatar = request.FILES.get('avatar')
        if avatar:
            if profile.avatar is None:
                profile.avatar = Avatar.objects.create(src=avatar, alt="User Avatar")
            else:
                profile.avatar.src = avatar
                profile.avatar.save()
            profile.save()

        profile.save()
        return Response(ProfileSerializer(profile, context={'request': request}).data)


class ProfileAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Обновляет аватар пользователя"""
        profile = Profile.objects.get(user=request.user)

        avatar = request.FILES.get('avatar')

        if avatar:
            if not profile.avatar:
                avatar_instance = Avatar.objects.create(src=avatar, alt="User Avatar")
                profile.avatar = avatar_instance
            else:
                profile.avatar.src = avatar
                profile.avatar.alt = "Updated User Avatar"
            profile.avatar.save()
            profile.save()
            return Response({"message": "Avatar updated successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "No avatar uploaded"}, status=status.HTTP_400_BAD_REQUEST)


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