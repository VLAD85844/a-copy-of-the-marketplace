from rest_framework import serializers
from .models import Profile, Avatar


class AvatarSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj):
        if obj.src:
            return self.context['request'].build_absolute_uri(obj.src.url)
        return None


class ProfileSerializer(serializers.ModelSerializer):
    avatar = AvatarSerializer()

    class Meta:
        model = Profile
        fields = ["fullName", "phone", "avatar", "email"]

    def update(self, instance, validated_data):
        avatar_data = validated_data.pop('avatar', None)
        if avatar_data:
            if not instance.avatar:
                instance.avatar = Avatar.objects.create(**avatar_data)
            else:
                for attr, value in avatar_data.items():
                    setattr(instance.avatar, attr, value)
                instance.avatar.save()

        instance.fullName = validated_data.get('fullName', instance.fullName)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance