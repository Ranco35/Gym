from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/training_session/(?P<session_id>\w+)/$', consumers.TrainingSessionConsumer.as_asgi()),
] 