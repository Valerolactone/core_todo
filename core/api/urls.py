from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminProjectActivationView,
    AdminProjectViewSet,
    AdminTaskActivationView,
    AdminTaskViewSet,
    ProjectParticipantsViewSet,
    ProjectViewSet,
    TasksAttachmentsViewSet,
    TaskSubscribersViewSet,
    TaskViewSet,
)

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
]

urlpatterns += router.urls
