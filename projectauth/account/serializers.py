import bcrypt
from rest_framework import serializers
from .models import User, Role, BusinessElement, AccessRule


class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, required=False, default='')
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        default_role = Role.objects.get(name='user')
        return User.objects.create(
            password_hash=password_hash,
            role=default_role,
            **validated_data,
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    role = serializers.StringRelatedField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'role', 'is_active', 'created_at']


class ProfileUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    middle_name = serializers.CharField(max_length=100, required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6, write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)

    def validate(self, data):
        if 'password' in data or 'password_confirm' in data:
            if data.get('password') != data.get('password_confirm'):
                raise serializers.ValidationError({"password_confirm": "Пароли не совпадают."})
        return data

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        return value

    def update(self, instance, validated_data):
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        instance.save()
        return instance


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = ['id', 'code', 'name', 'description']


class AccessRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_code = serializers.CharField(source='element.code', read_only=True)

    class Meta:
        model = AccessRule
        fields = [
            'id', 'role', 'role_name', 'element', 'element_code',
            'can_read', 'can_read_all', 'can_create',
            'can_update', 'can_update_all', 'can_delete', 'can_delete_all',
        ]
