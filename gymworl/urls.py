from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gym_tracker.urls')),
    path('trainers/', include('trainers.urls', namespace='trainers')),  # Incluir namespace
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 