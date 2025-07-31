# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import JobCreateSerializer,EmployeeStatsSerializer,JobStatsSerializer
from django.db.models import Count,Sum,Avg
from django.contrib.auth import get_user_model
from .models import Job

User=get_user_model()

class JobCreateView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JobCreateSerializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save()
            # print("serializer data",serializer.data)
            return Response({"status": "success", "job_id": job.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#total jobs per employees
class TotalJobsPerEmployerView(APIView):
    def get(self,request):
        total_jobs_per_employer=User.objects.filter(is_employer=True).annotate(total_jobs=Count('jobs'))        #annotate will add a temporary column named total_jobs with value of total jobs for user
        # print(total_jobs_per_employer)
        # for e in total_jobs_per_employer:
        #     print(e.username, e.total_jobs)
        serializer=EmployeeStatsSerializer(total_jobs_per_employer,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
#Total earnings per freelancer
class TotalEarningPerFreelancerView(APIView):
    def get(self,request):
        total_earnings_per_user=User.objects.filter(is_freelancer=True).annotate(total_earnings=Sum('freelancer__milestones__amount'))
        serializer=EmployeeStatsSerializer(total_earnings_per_user,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
#average milestone value per job
class AvgMilestonePerJobView(APIView):
    def get(self,request):
        avg_milestone_per_job=Job.objects.annotate(avg_milestone=Avg("milestones__amount"))
        serializer=JobStatsSerializer(avg_milestone_per_job,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

#Jobs with unapproved but completed milestones
class JobsUnapprovedView(APIView):
    def get(self,request):
        pending_jobs_qs=Job.objects.filter(milestones__is_approved_by_employer=False,milestones__is_completed_by_freelancer=True).distinct()
        print("pending jobs querysets are:",pending_jobs_qs)
        serializer=JobStatsSerializer(pending_jobs_qs,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)