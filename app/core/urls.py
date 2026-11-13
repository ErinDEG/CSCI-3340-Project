from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('events/', views.events, name='events'),
    # path('lost-found/', views.lostfound, name='lost-found'),
    
]