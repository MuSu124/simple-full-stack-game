from django.urls import path

from . import views


urlpatterns = [
    path("", views.characters, name="characters"),
    path(
        "<int:character_id>/upgrade/",
        views.upgrade_character,
        name="upgrade_character",
    ),
]
