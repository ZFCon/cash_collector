from django.urls import path

from .views import CollectView, NextTaskView, PayView, StatusView, TaskListView

urlpatterns = [
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("next_task/", NextTaskView.as_view(), name="next-task"),
    path("status/", StatusView.as_view(), name="status"),
    path("collect/", CollectView.as_view(), name="collect"),
    path("pay/", PayView.as_view(), name="pay"),
]
