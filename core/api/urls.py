from api.views import (
    AdminProjectActivationView,
    AdminProjectViewSet,
    AdminTaskActivationView,
    AdminTaskViewSet,
    ProjectParticipantsViewSet,
    ProjectViewSet,
    TaskExecutorUpdateView,
    TasksAttachmentsViewSet,
    TaskStatusUpdateView,
    TaskSubscribersViewSet,
    TaskViewSet,
)
from django.urls import path
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'admin_projects', AdminProjectViewSet, basename='admin_project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'admin_tasks', AdminTaskViewSet, basename='admin_task')
router.register(
    r'task_subscriptions', TaskSubscribersViewSet, basename='task_subscription'
)
router.register(
    r'project_participants', ProjectParticipantsViewSet, basename='project_participant'
)
router.register(
    r'task_attachments', TasksAttachmentsViewSet, basename='task_attachment'
)

urlpatterns = [
    path(
        'admin_project_activation/<int:pk>/',
        AdminProjectActivationView.as_view(),
        name='admin_project_activation',
    ),
    path(
        'admin_task_activation/<int:pk>/',
        AdminTaskActivationView.as_view(),
        name='admin_task_activation',
    ),
    path(
        'task_status_update/<int:pk>/',
        TaskStatusUpdateView.as_view(),
        name='task_status_update',
    ),
    path(
        'task_executor_update/<int:pk>/',
        TaskExecutorUpdateView.as_view(),
        name='task_executor_update',
    ),
]

urlpatterns += router.urls
