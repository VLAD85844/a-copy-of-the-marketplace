from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile, Avatar
from django.contrib.auth.hashers import make_password


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': _('Логин'),
        }


class CustomUserChangeForm(UserChangeForm):
    new_password = forms.CharField(
        label=_("Новый пароль"),
        required=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=_("Введите новый пароль и сохраните пользователя."),
    )

    class Meta:
        model = User
        fields = ('username', 'new_password')
        labels = {
            'username': _('Логин'),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    model = User
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('username', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username',)
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'new_password')}),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullName', 'email', 'phone', 'avatar')
    search_fields = ('user__username', 'fullName', 'email', 'phone')
    list_filter = ('user__is_active',)
    fields = ('user', 'fullName', 'email', 'phone', 'avatar')


class AvatarAdmin(admin.ModelAdmin):
    exclude = ('alt',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Avatar, AvatarAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)