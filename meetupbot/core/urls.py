from django.urls import path
from . import views


urlpatterns = [
    # одна простая заглушка, чтобы Django был доволен
    path('', views.healthcheck, name='healthcheck'),
]
