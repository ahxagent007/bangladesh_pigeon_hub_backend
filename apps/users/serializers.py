from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from apps.marketplace.models import Review

User = get_user_model()


def _abs_avatar(obj, context):
    req = context.get('request')
    if obj.avatar:
        url = obj.avatar.url
        if req and not url.startswith('http'):
            return req.build_absolute_uri(url)
        return url
    return None


class UserSerializer(serializers.ModelSerializer):
    """Own profile (/api/auth/me/) — includes editable + social fields."""
    listing_count   = serializers.ReadOnlyField()
    avg_rating      = serializers.ReadOnlyField()
    follower_count  = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'phone', 'location', 'bio', 'avatar', 'language',
                  'listing_count', 'avg_rating', 'follower_count',
                  'following_count', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'username', 'email', 'date_joined', 'is_verified')


class PublicUserSerializer(serializers.ModelSerializer):
    full_name       = serializers.ReadOnlyField()
    avg_rating      = serializers.ReadOnlyField()
    follower_count  = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    listing_count   = serializers.ReadOnlyField()
    avatar          = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'location', 'bio', 'avatar',
                  'is_verified', 'avg_rating', 'follower_count',
                  'following_count', 'listing_count', 'date_joined')

    def get_avatar(self, obj):
        return _abs_avatar(obj, self.context)


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name   = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ('id', 'rating', 'comment', 'reviewer_name',
                  'reviewer_avatar', 'created_at')
        read_only_fields = ('id', 'created_at')

    def get_reviewer_avatar(self, obj):
        return _abs_avatar(obj.reviewer, self.context)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2',
                  'first_name', 'last_name', 'location', 'phone')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
