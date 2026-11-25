from django.urls import path

from . import views


urlpatterns = [
    path("", views.list_events, name="event_list"),
    path("add_event/", views.event_form, name="add_event"),
    path("<int:pk>/edit/", views.event_form, name="edit_event"),
    path("subscriptions/", views.subscriptions, name="event_subscriptions"),
    path(
        "subscriptions/<str:category>/",
        views.update_subscription,
        name="update_event_subscription",
    ),
]
