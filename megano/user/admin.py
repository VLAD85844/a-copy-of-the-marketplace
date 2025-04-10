from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Avatar

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'fullName', 'email', 'phone', 'balance', 'avatar')
    search_fields = ('user__username', 'fullName', 'email', 'phone')
    list_filter = ('user__is_active', 'balance')
    fields = ('user', 'fullName', 'email', 'phone', 'balance', 'avatar')

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']
    filter_horizontal = ()

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email'),
        }),
    )

admin.site.register(Profile, ProfileAdmin)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Avatar)

admin.site.unregister(User)
admin.site.unregister(Group)