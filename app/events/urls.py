from django.urls import path
from . import views


urlpatterns= [
    # Very crucial. Turning these into comments will not allow the urls to be joinable!
    path('', views.list_events, name= 'event_list'),
    path('add_event/', views.add_events, name='add_event'),
]