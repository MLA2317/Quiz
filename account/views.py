from django.shortcuts import render
from rest_framework import generics, status, serializers, permissions
from .models import Account
from rest_framework.response import Response
from .serializer import RegisterSerializer, LoginSerializer, MyProfileSerializer


class RegisterCreateApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data': "Account successfully created"}, status=status.HTTP_201_CREATED)


class LoginCreateApi(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'tokens': serializer.data['tokens']}, status=status.HTTP_200_OK)


class MyProfileList(generics.GenericAPIView):
    serializer_class = MyProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        query = Account.objects.get(id=user.id)
        serializer = self.serializer_class(query)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)








