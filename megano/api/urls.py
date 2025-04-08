from django.urls import path
from . import views

urlpatterns = [

    path("profile", views.ProfileView.as_view(), name="profile"),
    path("sign-in", views.SignInView.as_view(), name="sign-in"),
    path("sign-up", views.SignUpView.as_view(), name="sign-up"),

]

