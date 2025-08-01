from django.urls import path,include
from .  import views

urlpatterns = [
    path('create/',views.JobCreateView.as_view()),
    path('totaljobsperemployer/',views.TotalJobsPerEmployerView.as_view()),
    path('totalearningperfreelancer/',views.TotalEarningPerFreelancerView.as_view()),
    path('avgmilestoneperjob/',views.AvgMilestonePerJobView.as_view()),
    path('jobsunapproved/',views.JobsUnapprovedView.as_view()),
    # path('users/', include("portal.urls")),
]

#for update

urlpatterns+=[
    path('freelancercompletemilestone/<str:pk>/',views.CompleteMilestoneView.as_view()),
    path('employerapprovemilestone/<str:pk>/',views.ApproveMilestoneView.as_view()),
]