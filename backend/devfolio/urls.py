from django.urls import path
from .views import Devfolio

urlpatterns = [
    path('project/', Devfolio.as_view(), name='devfolio'),
]
