# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer,AddSkillSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from django.db import transaction
User=get_user_model()

class UserRegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=status.HTTP_201_CREATED)
        print("serializer is not valid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class LoginAPI(APIView):
    def post(self,request):
        try:         
            try:
                # logging.info("Enter into the if block of serializer valid")
                print("user email is :",request.data['email'])
                user=User.objects.get(email=request.data['email'])  #getting user based upon email from db because in authenticate username is required not email
                print("user is ---",user)
            except Exception as e:
                return Response({ 'message':f"User not found for {request.data['email']}",
                        'data':str(e)},
                        status=status.HTTP_404_NOT_FOUND)
        
            user=authenticate(username=user.username, password=request.data['password'])  #returns authenticated user if exists or none
            if user:
                # logging.info("User details authenticated successfully")
                refresh=RefreshToken.for_user(user)    #manually token generated here
                # logging.info(f"Token generated for user")
                # print("refresh token--",str(refresh))
                return Response({
                    "message":"Login Successful",
                    "data":{
                        "access_token":str(refresh.access_token),
                        "refresh_token":str(refresh)
                    }
                },status=status.HTTP_200_OK)
            else:
                # logging.warning(f"Invalid credentials")
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
            if employer.username == "default":
                return Response({"error": "Cannot delete the default employer."}, status=status.HTTP_400_BAD_REQUEST)

            employer.delete()  # This triggers the signal

            return Response({"status": "Employer soft-deleted and jobs reassigned."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Employer not found."}, status=status.HTTP_404_NOT_FOUND)


class AddSkillView(APIView):
    permission_classes=[permissions.IsAdminUser]
    
    def post(self,request):
        try:
            serializer=AddSkillSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response("skill created successfully.",status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(f"error {str(e)}",status=status.HTTP_400_BAD_REQUEST)