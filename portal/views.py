# users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomUserSerializer,EmployeeSoftDeleteSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions

User=get_user_model()

class UserRegisterView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'User created successfully', 'user_id': user.id}, status=status.HTTP_201_CREATED)
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
        
    
# class DeleteUserView(APIView):
#     permission_classes=[permissions.IsAdminUser]
#     def delete(self,request,pk):
#         try:
#             user=User.objects.get(id=pk)
#         except Exception as e:
#             return Response(f"no user with id {pk}")
        
#         user.is_deleted=True
#         user.save()

#         return Response("user deleted successfully.")
    



class EmployerSoftDeleteAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_employer=True)
        except User.DoesNotExist:
            return Response({"detail": "Employer not found."}, status=404)

        serializer = EmployeeSoftDeleteSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Employer soft deleted and jobs reassigned."})
        return Response(serializer.errors, status=400)
