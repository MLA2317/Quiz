from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
     TokenObtainPairView,
     TokenRefreshView,
     TokenBlacklistView,
)


urlpatterns = [
    path('register/', views.RegisterCreateApi.as_view()),
    path('login/', views.LoginCreateApi.as_view()),
    path('myprofile/', views.MyProfileList.as_view()),

    # refresh token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]
