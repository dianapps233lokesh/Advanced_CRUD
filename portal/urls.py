from django.urls import path,include
from .  import views

urlpatterns = [
    path('create/',views.UserRegisterView.as_view()),
    path('login/',views.LoginAPI.as_view()),
    path('soft_delete/<str:pk>/',views.EmployerSoftDeleteView.as_view()),
]


urlpatterns+=[
    path('skill/add/',views.AddSkillView.as_view()),
    path('delete/',views.UserDeleteView.as_view()),
]