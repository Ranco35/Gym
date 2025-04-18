# gym_tracker/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from gym_tracker.views import home_view, csrf_failure, current_user_view
from gym_tracker.exercises.urls import api_patterns as exercises_api_patterns, web_urlpatterns as exercises_web_patterns

# Página de login personalizada
def serve_login_page(request):
    return render(request, 'login.html')

# Definimos directamente las rutas de autenticación
auth_urlpatterns = [
    path('login/', csrf_exempt(auth_views.LoginView.as_view(template_name='login.html')), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Usar autenticación estándar de Django con csrf_exempt para desarrollo
    path('accounts/', include((auth_urlpatterns, 'accounts'), namespace='accounts')),
    path('login/', serve_login_page, name='custom_login'),
    
    # Rutas de la interfaz web
    path('exercises/', include((exercises_web_patterns, 'exercises'), namespace='exercises')),
    path('workouts/', include('gym_tracker.workouts.urls', namespace='workouts')),
    path('trainings/', include('gym_tracker.trainings.urls', namespace='trainings')),
    
    # Ruta para el área de entrenadores
    path('trainers/', include('trainers.urls', namespace='trainers')),
    
    # API endpoints
    path('api/exercises/', include((exercises_api_patterns, 'exercises_api'), namespace='exercises_api')),
    path('api/users/', include('gym_tracker.users.urls', namespace='users')),
    path('stats/', include('gym_tracker.stats.urls')),  # Nueva URL para estadísticas
    
    # Rutas para la PWA
    path('pwa/', include('gym_tracker.pwa.urls', namespace='pwa')),
    path('', include('pwa.urls')),  # Para manifest.json y service worker
]

# Siempre servir archivos estáticos para el desarrollo local
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Añadimos la ruta principal para renderizar la página principal con el dashboard
urlpatterns += [
    path('', home_view, name='home'),
    path('api/user/', current_user_view, name='current-user'),
]
