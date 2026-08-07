from django.urls import path

from . import views


urlpatterns = [
    path(
        "cnvz/",
        views.upload_rapport_cnvz,
        name="upload_rapport_cnvz",
    ),
]
