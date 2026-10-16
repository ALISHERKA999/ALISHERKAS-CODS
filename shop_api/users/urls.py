
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, ConfirmView, LoginView
from .serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('confirm/', ConfirmView.as_view()),
    path('login/', LoginView.as_view()),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

