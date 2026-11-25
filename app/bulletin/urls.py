from django.urls import path

from . import views


app_name = "bulletin"
urlpatterns = [
    path("", views.board, name="board"),
    path("new/", views.announcement_form, name="post"),
    path("<int:pk>/edit/", views.announcement_form, name="edit"),
]
