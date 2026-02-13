from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("khalti/initiate/", views.khalti_initiate, name="khalti_initiate"),
    path("khalti/callback/", views.khalti_callback, name="khalti_callback"),
]
