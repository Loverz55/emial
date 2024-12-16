from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SendEmailView, 
    EmailHistoryView,
    EmailTemplateViewSet,
    EmailImageUploadView
)

router = DefaultRouter()
router.register(r'templates', EmailTemplateViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('send/', SendEmailView.as_view(), name='send-email'),
    path('history/', EmailHistoryView.as_view(), name='email-history'),
    path('upload/image/', EmailImageUploadView.as_view(), name='upload-image'),
] 