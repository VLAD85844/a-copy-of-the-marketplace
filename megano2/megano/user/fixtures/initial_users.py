import os
from django.core.files import File
from django.contrib.auth.models import User
from user.models import Profile, Avatar


def create_initial_user():
    user = User.objects.create_user(
        username="annoying_orange",
        email="no-reply@mail.ru",
        password="123456"
    )

    avatar_path = "media/app_users/avatars/user_avatars/fab7087cf712eab8bab164ed06a7c31e.jpg"

    if os.path.exists(avatar_path):
        with open(avatar_path, 'rb') as f:
            avatar = Avatar.objects.create(
                alt="Image alt string"
            )
            avatar.src.save(os.path.basename(avatar_path), File(f))
            avatar.save()
            profile = Profile.objects.create(
                user=user,
                fullName="Annoying Orange",
                phone="88002000600",
                email="no-reply@mail.ru",
                avatar=avatar
            )
            print(f"Created user: {profile.fullName}")
    else:
        print(f"Avatar image not found at: {avatar_path}")
        profile = Profile.objects.create(
            user=user,
            fullName="Annoying Orange",
            phone="88002000600",
            email="no-reply@mail.ru"
        )
        print(f"Created user without avatar: {profile.fullName}")

if __name__ == "__main__":
    create_initial_user()