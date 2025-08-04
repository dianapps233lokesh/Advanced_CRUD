from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import JobCreateSerializer,EmployeeStatsSerializer,JobStatsSerializer
from django.db.models import Count,Sum,Avg
from django.contrib.auth import get_user_model
from .models import Job,Milestone
from django.db import transaction

User=get_user_model()

class JobCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        if not request.user.is_employer:
            return Response("only employer can create jobs",status=status.HTTP_400_BAD_REQUEST)
        serializer = JobCreateSerializer(data=request.data,context={'request':request})

        if serializer.is_valid():
            job = serializer.save()
            # print("serializer data",serializer.data)
            return Response({"status": "success", "job_id": job.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#total jobs per employees
class TotalJobsPerEmployerView(APIView):
    def get(self,request):
        try:
            total_jobs_per_employer=User.objects.filter(is_employer=True).annotate(total_jobs=Count('jobs'))        #annotate will add a temporary column named total_jobs with value of total jobs for user
            serializer=EmployeeStatsSerializer(total_jobs_per_employer,many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response()
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
    

#Complete milestone view

class CompleteMilestoneView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,pk):
        try:
            print("pk---",pk)
            milestone=Milestone.objects.get(id=pk)
        except Exception as e:
            return Response(f"no milestone found with the id {pk}")
        # print("request.user")
        if milestone.job.freelancer!=request.user:
            return Response(f"{request.user} freelancer is not assigned to this milestone")
        
        milestone.is_completed_by_freelancer=True
        milestone.save()

        return Response(f"status changed {milestone.is_completed_by_freelancer}",status=status.HTTP_202_ACCEPTED)
    
class ApproveMilestoneView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,pk):
        try:
            print("pk---",pk)
            milestone=Milestone.objects.get(id=pk)
        except Exception as e:
            return Response(f"no milestone found with the id {pk}")
        
        if not milestone.is_completed_by_freelancer:
            return Response("milestone is not completed by the freelancer")
        
        if milestone.job.employer!=request.user:
            return Response("employer not associated with the job to which milestone is related")

        milestone.is_approved_by_employer=True
        milestone.save()

        return Response(f"status changed {milestone.is_approved_by_employer}")
    

class AssignFreelancerToJobAPIView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,job_id):
        try:
            job=Job.objects.get(id=job_id)
        except Exception as e:
            return Response(f"no job found for the id {job_id}",status=status.HTTP_404_NOT_FOUND)
        req_skills=job.skills.all()
        print("required skills are:",req_skills)
        if job.freelancer:
            return Response("Job has already been assigned a freelancer.")
        
        freelancers=User.objects.filter(is_freelancer=True,skill__in=req_skills,is_deleted=False).annotate(match_skill_count=Count('skill')).order_by('-match_skill_count').distinct()
        print("all freelancers",freelancers)
        if not freelancers:
            return Response("No freelancer found for this job",status=status.HTTP_404_NOT_FOUND)

        job.freelancer=freelancers.first()  # this will pick the best freelancer 
        print(f"the best freelancer is {freelancers.first()}")
        job.save()

        return Response("successfully assigned freelancer to job",status=status.HTTP_200_OK)


        