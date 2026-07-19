from rest_framework import generics, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Follow
from .serializers import (
    RegisterSerializer, UserSerializer, PublicUserSerializer, ReviewSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser, JSONParser]  # allow avatar upload

    def get(self, request):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteAccountView(APIView):
    """Permanently delete the authenticated user's account (App Store 5.1.1)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        password = request.data.get('password') or ''
        if not request.user.check_password(password):
            return Response({'password': ['Incorrect password.']}, status=400)

        request.user.delete()
        return Response(status=204)


class PublicProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, username):
        from apps.marketplace.models import Listing, Review
        from apps.marketplace.serializers import ListingSerializer

        user = get_object_or_404(User, username=username)
        listings = (Listing.objects.filter(seller=user, status='active')
                    .select_related('pigeon__breed')
                    .prefetch_related('pigeon__images')[:12])
        reviews = Review.objects.filter(seller=user).select_related('reviewer')[:20]

        is_following = False
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=request.user, following=user).exists()

        ctx = {'request': request}
        return Response({
            'user':        PublicUserSerializer(user, context=ctx).data,
            'is_following': is_following,
            'is_me':       request.user.is_authenticated and request.user == user,
            'listings':    ListingSerializer(listings, many=True, context=ctx).data,
            'reviews':     ReviewSerializer(reviews, many=True, context=ctx).data,
        })


class ToggleFollowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        target = get_object_or_404(User, username=username)
        if target == request.user:
            return Response({'error': "You can't follow yourself."}, status=400)

        follow, created = Follow.objects.get_or_create(
            follower=request.user, following=target)
        if not created:
            follow.delete()
            following = False
        else:
            following = True
            from apps.notifications.models import notify
            notify(target, request.user, 'follow',
                   f'{request.user.username} started following you.',
                   f'/users/{request.user.username}/')

        return Response({'following': following, 'follower_count': target.follower_count})


class UserReviewsView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, username):
        from apps.marketplace.models import Review
        seller = get_object_or_404(User, username=username)
        reviews = Review.objects.filter(seller=seller).select_related('reviewer')
        return Response(
            ReviewSerializer(reviews, many=True, context={'request': request}).data)

    def post(self, request, username):
        from apps.marketplace.models import Review
        seller = get_object_or_404(User, username=username)
        if seller == request.user:
            return Response({'error': "You can't review yourself."}, status=400)

        rating  = request.data.get('rating')
        comment = (request.data.get('comment') or '').strip()
        if not rating or not comment:
            return Response({'error': 'Rating and comment are required.'}, status=400)

        review, created = Review.objects.update_or_create(
            reviewer=request.user, seller=seller,
            defaults={'rating': rating, 'comment': comment})

        if created:
            from apps.notifications.models import notify
            notify(seller, request.user, 'review',
                   f'{request.user.username} left you a {rating}★ review.',
                   f'/users/{seller.username}/')

        return Response(
            ReviewSerializer(review, context={'request': request}).data, status=201)
