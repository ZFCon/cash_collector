from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CashCollector, Collection, Payment, Task
from .serializers import (CollectionSerializer, PaymentSerializer,
                          TaskSerializer)


class TaskListView(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class NextTaskView(APIView):
    def get(self, request, *args, **kwargs):
        collector = CashCollector.objects.get(user=request.user)
        next_task = (
            Task.objects.filter(collection__cash_collector=collector)
            .order_by("amount_due_at")
            .first()
        )
        serializer = TaskSerializer(next_task)
        return Response(serializer.data)


class StatusView(APIView):
    def get(self, request, *args, **kwargs):
        collector = CashCollector.objects.get(user=request.user)
        return Response({"is_frozen": collector.is_frozen})


class CollectView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PayView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
