from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmailTaskViewSet

router = DefaultRouter()
router.register('', EmailTaskViewSet, basename='email-task')

urlpatterns = [
    path('', include(router.urls)),
] 