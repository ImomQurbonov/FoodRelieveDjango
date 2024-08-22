import os, requests
from allauth.account.forms import default_token_generator
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.views import get_user_model
from dj_rest_auth.registration.views import SocialLoginView
from jwt.utils import force_bytes
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from yaml import serialize
from .tests import send_email_reset
from .models import ProfilesImage
from .serializers import (
    UserRegisterSerializer, UserProfileImageSerializer,
    UserSerializer, PasswordResetSerializer,
    GoogleRedirectSerializer, FacebookRedirectSerializer,
    ProfileViewSerializer
)
from dotenv import load_dotenv

load_dotenv()
User = get_user_model()


class RegisterAPIView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)


# Log out
class LogoutAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response(status=204)


# User Info
class UserInfoAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        return Response({'success': True, 'data': user_serializer.data})


# PasswordResetRequest
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            send_email_reset.delay(
                email,
                uid,
                token,
            )
            return Response({'detail': 'Password reset link sent to your email.'}, status=202)
        else:
            return Response({'detail': 'Email not found.'}, status=404)


# PasswordResetConfirm
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, uidb64, token, *args, **kwargs):
        try:
            uidb64 = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uidb64)

            if default_token_generator.check_token(user, token):
                new_password = request.data.get('new_password', '')
                user.set_password(new_password)
                user.save()
                return Response({'detail': 'Password reset successful.'}, status=200)
            else:
                return Response({'detail': 'Invalid token.'}, status=400)
        except Exception as e:
            return Response({'detail': f'{e}.'}, status=400)


# Google sign-in
class RedirectToGoogleAPIView(generics.GenericAPIView):
    serializer_class = GoogleRedirectSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Invalid parameters'}, status=status.HTTP_400_BAD_REQUEST)
        google_redirect_uri = serializer.validated_data['google_redirect_uri']
        try:
            google_client_id = SocialApp.objects.get(provider='google').client_id
        except SocialApp.DoesNotExist:
            return Response({'success': False, 'message': 'SocialApp does not exist'}, status=status.HTTP_404_NOT_FOUND)
        url = f'https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={google_redirect_uri}&prompt=consent&response_type=code&client_id={google_client_id}&scope=openid email profile&access_type=offline'
        return redirect(url)


class GoogleLogin(SocialLoginView): # if you want to use Authorization Code Grant, use this
    adapter_class = GoogleOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/accounts/google/callback'
    client_class = OAuth2Client


@api_view(["GET"])
def callback_google(request):
    code = request.GET.get("code")
    res = requests.post("http://127.0.0.1:8000/accounts/google", data={"code": code}, timeout=30)
    print('Response >>>', res.json())
    return Response(res.json())


# facebook
class RedirectToFacebookApiView(generics.GenericAPIView):
    serializer_class = FacebookRedirectSerializer

    def get(self, request):
        serializer = self.get_serializer(data=request.query_params)
        if not serializer.is_valid():
            return Response({'success': False, 'message': 'Invalid parameters'}, status=400)

        facebook_redirect_uri = serializer.validated_data.get('facebook_redirect_uri', os.getenv('FACEBOOK_REDIRECT_URI'))
        facebook_app_id = serializer.validated_data.get('facebook_app_id', os.getenv('FACEBOOK_APP_ID'))

        if not facebook_redirect_uri or not facebook_app_id:
            return Response({'success': False, 'message': 'Missing Facebook app credentials'}, status=400)

        url = (
            f'https://www.facebook.com/v9.0/dialog/oauth?'
            f'client_id={facebook_app_id}&redirect_uri={facebook_redirect_uri}&scope=email,public_profile'
        )

        return redirect(url)


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/accounts/facebook/callback_facebook"
    client_class = OAuth2Client


@api_view(['GET'])
def callback_facebook(request):
    code = request.query_params.get('code')
    if not code:
        return Response({'error': 'Code parameter is missing.'})
    try:
        response = requests.get("https://graph.facebook.com/v9.0/oauth/access_token", params={
            'client_id': os.getenv('FACEBOOK_APP_ID'),
            'redirect_uri': os.getenv('FACEBOOK_REDIRECT_URI'),
            'client_secret': os.getenv('FACEBOOK_APP_SECRET'),
            'code': code,
        })
        response.raise_for_status()
        data = response.json()
        access_token = data.get('access_token')

        if access_token:
            user_info_response = requests.get("https://graph.facebook.com/me", params={
                'fields': 'id,name,email',
                'access_token': access_token,
            })
            user_info_response.raise_for_status()
            user_info = user_info_response.json()
            return Response({'access_token': access_token, 'user_info': user_info})
        else:
            return Response({'error': 'Access token not found.'})
    except requests.exceptions.RequestException as e:
        return Response({'error': str(e)})


class UserProfileImageAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileImageSerializer

    def post(self, request):
        user = request.user
        image = request.data.get('image')

        if not image:
            return Response({"error": "Image field is required."}, status=400)

        profile_image = ProfilesImage.objects.create(
            user=user,
            image=image,
        )
        profile_serializer = UserProfileImageSerializer(profile_image)
        return Response(profile_serializer.data, status=201)


class ProfileViewAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProfileViewSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=200)































