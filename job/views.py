from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import JobCreateSerializer,EmployeeStatsSerializer,JobStatsSerializer
from django.db.models import Count,Sum,Avg,Q
from django.contrib.auth import get_user_model
from .models import Job,Milestone
from django.db import transaction
from rest_framework.decorators import api_view,permission_classes
import csv
from django.http import StreamingHttpResponse
from utils.logger import logging



User=get_user_model()

class JobCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            if not request.user.is_employer or request.user.is_deleted:
                return Response({ 
                            'message': 'Only employer can post jobs. User not an employer or user is deleted',
                            'data':request.user
                            },status=status.HTTP_400_BAD_REQUEST)
            serializer = JobCreateSerializer(data=request.data,context={'request':request})

            if serializer.is_valid():
                job = serializer.save()
                logging.info(f"job created successfully. job id is {job.id}")
                return Response({
                    'message':"Job created successfully",
                    'data':serializer.data
                },status=status.HTTP_201_CREATED)
            return Response({ 
                            # 'message': 'error',
                            'data':serializer.errors
                            },status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({ 
                            'message': 'error',
                            'data':str(e)
                            },status=status.HTTP_400_BAD_REQUEST)

#total jobs per employees
class TotalJobsPerEmployerView(APIView):

    def get(self,request):
        try:
            total_jobs_per_employer=User.objects.filter(is_employer=True).annotate(total_jobs=Count('jobs'))        #annotate will add a temporary column named total_jobs with value of total jobs for user
            serializer=EmployeeStatsSerializer(total_jobs_per_employer,many=True)
            return Response({
                'message':"total jobs per employer fetched successfully",
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 
                        'message': f'error {str(e)}',
                        'data':serializer.errors
                        },status=status.HTTP_400_BAD_REQUEST)
        
#Total earnings per freelancer
class TotalEarningPerFreelancerView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        try:
            logging.info(f"id for the current user is {request.user.id}")
            total_earnings_per_user=User.objects.filter(is_freelancer=True,freelancer__employer=request.user).annotate(total_earnings=Sum('freelancer__milestones__amount',filter=Q(freelancer__employer=request.user)))
            # logging.info(f"total earnninig per employer is: {total_earnings_per_user}")
            serializer=EmployeeStatsSerializer(total_earnings_per_user,many=True)
            return Response({
                'message':"total earnings per freelancer",
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except  Exception as e:
            return Response({ 
                        # 'message': f'error {str(e)}',
                        'data':str(e)
                        },status=status.HTTP_400_BAD_REQUEST)

#average milestone value per job
class AvgMilestonePerJobView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        try:
            logging.info(f"current user id is {request.user}")
            avg_milestone_per_job=Job.objects.filter(employer=request.user).annotate(avg_milestone=Avg("milestones__amount"))
            logging.info(f"Avg milestone per job {avg_milestone_per_job}")
            serializer=JobStatsSerializer(avg_milestone_per_job,many=True)
            logging.info(f"serializer datta: {serializer.data}")
            return Response({
                # 'message':"avg milestone value per job ",
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 
                        # 'message': f'error {str(e)}',
                        'data':str(e)
                        },status=status.HTTP_400_BAD_REQUEST)

#Jobs with unapproved but completed milestones
class JobsUnapprovedView(APIView):
    def get(self,request):
        try:
            pending_jobs_qs=Job.objects.filter(milestones__is_approved_by_employer=False,milestones__is_completed_by_freelancer=True).distinct()
            logging.info(f"pending jobs querysets are: {pending_jobs_qs}")
            serializer=JobStatsSerializer(pending_jobs_qs,many=True)
            return Response({
                'message':"completed jobs but are unapproved",
                'data':serializer.data
            },status=status.HTTP_200_OK)
        except  Exception as e:
            return Response({ 
                        'message': f'error {str(e)}',
                        'data':serializer.errors
                        },status=status.HTTP_400_BAD_REQUEST)

#Complete milestone view
class CompleteMilestoneView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,pk):
        try:
            
            milestone=Milestone.objects.get(id=pk)
        except Exception as e:
            return Response({ 
                        'message': f'error. {str(e)}',
                        'data':None
                        },status=status.HTTP_404_NOT_FOUND)
     
        if milestone.job.freelancer!=request.user:
            return Response({ 
                        'message': 'this freelancer not assigned to this job',
                        'data':request.user.id
                        },status=status.HTTP_400_BAD_REQUEST)
        
        milestone.is_completed_by_freelancer=True
        milestone.save()

        return Response({
                'message':"complete the milestone from the freelancer",
                'data':{"milestone completed":True}
            },status=status.HTTP_200_OK)
    
class ApproveMilestoneView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request,pk):
        try:
            milestone=Milestone.objects.get(id=pk)
        except Exception as e:
            return Response({ 
                        'message': f'error. {str(e)}',
                        'data':None
                        },status=status.HTTP_404_NOT_FOUND)
        
        if not milestone.is_completed_by_freelancer:
            return Response({ 
                        'message': 'Milestone not completed by the freelancer',
                        'data':milestone.objects.all()
                        },status=status.HTTP_400_BAD_REQUEST)
        
        if milestone.job.employer!=request.user:
            return Response({ 
                        'message': 'this employer is not associated to this job',
                        'data':milestone.objects.all()
                        },status=status.HTTP_400_BAD_REQUEST)

        milestone.is_approved_by_employer=True
        milestone.save()

        return Response({
                'message':"approved milestone of the completed user",
                'data':{"milestone approved":True}
            },status=status.HTTP_200_OK)
    

class AssignFreelancerToJobAPIView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def post(self,request,job_id):
        try:
            job=Job.objects.get(id=job_id)
        except Exception as e:
            return Response({ 
                        'message': f'error. {str(e)}',
                        'data':None
                        },status=status.HTTP_404_NOT_FOUND)
        req_skills=job.skills.all()
        logging.info(f"required skills are: {req_skills}")
        if job.freelancer:
            return Response({ 
                        'message': 'freelancer already assigned to this job',
                        'data':job.freelancer.id
                        },status=status.HTTP_400_BAD_REQUEST)
        
        freelancers=User.objects.filter(is_freelancer=True,skill__in=req_skills,is_deleted=False).annotate(match_skill_count=Count('skill')).order_by('-match_skill_count').distinct()
        logging.info(f"all freelancers {freelancers}")
        if not freelancers:
            return Response({ 
                        'message': 'No freelancer found for this job',
                        'data':freelancers
                        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        job.freelancer=freelancers.first()  # this will pick the best freelancer 
        logging.info(f"the best freelancer is {freelancers.first()}")
        job.save()

        return Response({
                'message':"freelancer assigned successfully",
                'data':freelancers.first().username
            },status=status.HTTP_200_OK)


    
class Echo:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        return value


@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated]) 
def generate_archivejobs_csv(request):
    # Generator to stream rows
    def row_generator():
        yield ['job_id', 'title', 'description','is_archived']     #column names
        for job in Job.objects.all().iterator():     
            if job.is_archived:                           #iterator() using because generator loads one by one value into memory.
                yield [job.id, job.title, job.description, job.is_archived]         #values for columns defined above

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)

    response = StreamingHttpResponse((writer.writerow(row) for row in row_generator()), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="archived_jobs.csv"'
    
    return response


class CompleteMilestonesBulkUpdate(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def post(self,request):
        try:
            milestones_ids=request.data.get('milestone_ids',[])
            logging.info(f"milestones ids provided {milestones_ids}")
            if not milestones_ids:
                return Response({
                    'message':"No milestone ids provided",
                    'data':milestones_ids
                },status=status.HTTP_400_BAD_REQUEST)
            
            milestones=Milestone.objects.filter(id__in=milestones_ids,job__employer=request.user)
            logging.info(f"milestones objects for ids provided {milestones}")

            if not milestones:
                return Response({
                    'message':"No matching milestones found",
                    'data':milestones
                },status=status.HTTP_400_BAD_REQUEST)
            
            for milestone in milestones:
                milestone.is_completed_by_freelancer=True
            logging.info(f"milestones updated status {[milestone.is_completed_by_freelancer for milestone in milestones]}")
            Milestone.objects.bulk_update(milestones,['is_completed_by_freelancer'])
            logging.info("bulk updated successfully")
            return Response({
                    'message':f"{len(milestones)} marked as completed milestones",
                    'data':[milestone.is_completed_by_freelancer for milestone in milestones]
                },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message":str(e),
                "data":None
            },status=status.HTTP_400_BAD_REQUEST)
        

# RAW SQL View

class CompletedMilestonesRAW(APIView):
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        try:
            milestones=Milestone.objects.raw('''select m.id,m.title,m.amount 
                                             from 
                                             job_milestone as "m"
                                                join
                                             job_job as "j"
                                             on m.job_id=j.id where
                                             m.is_completed_by_freelancer=true and
                                             j.employer_id=%s
                                             ''',[request.user.id])
            data=[{
                "id": m.id,
                "title": m.title,
                "amount": float(m.amount)
            }
            for m in milestones]
            return Response({
                'data':data
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data':str(e)
            },status=status.HTTP_400_BAD_REQUEST)