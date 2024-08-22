from django.urls import path
from .views import *


urlpatterns = [
    path('register', RegisterAPIView.as_view(), name='register'),
    path('user-info', UserInfoAPIView.as_view(), name='user_info'),
    path('profile-view', ProfileViewAPIView.as_view(), name='profile'),
    # Google
    path('google', GoogleLogin.as_view(), name='google_login'),
    path('google-login', RedirectToGoogleAPIView.as_view(), name='google_login2'),
    path('google/callback', callback_google, name='google_callback'),
    # Facebook
    path('facebook', FacebookLogin.as_view(), name='facebook'),
    path('facebook-login', RedirectToFacebookApiView.as_view(), name='facebook-login'),
    path('facebook/callback', callback_facebook, name='facebook_callback'),
    path('reset-password', PasswordResetRequestView.as_view(), name='password_reset_request')
]