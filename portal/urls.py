from django.urls import path,include
from .  import views

urlpatterns = [
    path('create/',views.UserRegisterView.as_view()),
    path('login/',views.LoginAPI.as_view()),
    path('delete/<str:pk>/',views.EmployerSoftDeleteAPIView.as_view()),
]
