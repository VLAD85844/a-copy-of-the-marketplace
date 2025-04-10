from django.urls import path
from . import views

urlpatterns = [

    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("profile/avatar", views.ProfileAvatarView.as_view(), name="profile-avatar"),
    path("profile/password", views.UpdatePasswordView.as_view(), name="update-password"),
    path("sign-in", views.SignInView.as_view(), name="sign-in"),
    path("sign-up", views.SignUpView.as_view(), name="sign-up"),
    path('sign-out', views.signOut, name='sign-out'),

]

