from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from serializer import UserSerializer
from rest_framework import status
# Create your views here.
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
def index(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)
