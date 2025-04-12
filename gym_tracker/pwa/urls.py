from django.urls import path
from .views import GenerateImagesView

app_name = 'pwa'

urlpatterns = [
    path('generate-images/', GenerateImagesView.as_view(), name='generate-images'),
] 