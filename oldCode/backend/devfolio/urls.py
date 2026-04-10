from django.urls import path
from .views import Devfolio, Heartbeat, Stats

urlpatterns = [
    path('project/', Devfolio.as_view(), name='devfolio'),
    path('heartbeat/', Heartbeat, name='api_heartbeat'),
    path('stats/', Stats, name='api_stats'),
]
