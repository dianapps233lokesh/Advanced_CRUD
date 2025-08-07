from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer,AddSkillSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from django.db import transaction
from utils.logger import logging
from .models import CustomUser


User=get_user_model()

class UserRegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully', 'data': {"user":user.id}}, status=status.HTTP_201_CREATED)
        # logging("serializer is not valid")
        return Response({ 
                        'message': f'error',
                        'data':serializer.errors
                        },status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(APIView):
    def post(self,request):
        try:         
        
            # logging.info("Enter into the if block of serializer valid")
            logging.info(f"user email is : {request.data['email']}")
            user=User.objects.get(email=request.data['email'])  #getting user based upon email from db because in authenticate username is required not email
            logging.info(f"user is --- {user}")
       
        
            user=authenticate(username=user.username, password=request.data['password'])  #returns authenticated user if exists or none
            if user:
                logging.info("User details authenticated successfully")
                refresh=RefreshToken.for_user(user)    #manually token generated here
                logging.info(f"Token generated for user")
                return Response({
                    # "message":"Login Successful",
                    "data":{
                        "access_token":str(refresh.access_token),
                        "refresh_token":str(refresh)
                    }
                },status=status.HTTP_200_OK)
            else:
                logging.warning(f"Invalid credentials")
                return Response({ 'message':"wrong credentials provided",
                                 'data':None
                    },status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                { 
                        'message':"error occurred",
                        'data':str(e)
                },status=status.HTTP_400_BAD_REQUEST)
        

class EmployerSoftDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            employer = User.objects.get(pk=pk, is_employer=True, is_deleted=False)
            logging.info(f"employer is {employer} for the id {pk}")
            if employer.username == "default":
                return Response({ 
                        'message': f"can't delete the default employer",
                        'data':None
                        },status=status.HTTP_400_BAD_REQUEST)
            employer.soft_delete()  # This triggers the signal
            logging.info("Soft delete called and signal triggered")
            return Response({ 
                        'message': f'user soft delete and jobs reassigned using signal',
                        'data':None
                        },status=status.HTTP_200_OK)
        except Exception as e:
            return Response({ 
                        # 'message': 'error',
                        'data':str(e)
                        },status=status.HTTP_400_BAD_REQUEST)


class AddSkillView(APIView):
    permission_classes=[permissions.IsAdminUser]
    
    def post(self,request):
        try:
            serializer=AddSkillSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                logging.info("skill added successfully.")
            return Response({ 
                        # 'message': f'error {str(e)}',
                        'data':serializer.data
                        },status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({ 
                        'message': f'error {str(e)}',
                        'data':serializer.errors
                        },status=status.HTTP_400_BAD_REQUEST)
        
class UserDeleteView(APIView):
    permission_classes=[permissions.IsAuthenticated]

    def delete(self,request):
        try:
            user=User.objects.get(id=request.user.id)
            logging.info("user fetched successfuly. ")
            if user.username == "default":
                return Response({ 
                        'message': f"can't delete the default employer",
                        'data':None
                        },status=status.HTTP_400_BAD_REQUEST)
            user.delete()       #this will trigger an pre_delete signal
            logging.info("user deleted successfully")
            return Response({
                'message':"user deleted successfully",
                "data":None
            },status=
            status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'data':str(e),
            },status=status.HTTP_400_BAD_REQUEST)
        

class ActiveUsers(APIView):
    permission_classes=[permissions.IsAdminUser]
    def get(self,request):
        try:
            logging.info("Fetching all the active users")
            users=User.objects.all()
            logging.info(f"users are {users}")
            serializer=CustomUserSerializer(users,many=True)
            logging.info("Serializer created")
            # if serializer.is_valid():
            return Response({
                'data':serializer.data
            },
            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                    'data':str(e)
                },
                status=status.HTTP_400_BAD_REQUEST)