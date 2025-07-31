from django.urls import path,include
from .  import views

urlpatterns = [
    path('create/',views.UserRegisterView.as_view()),
    # path('users/', include("portal.urls")),
]
