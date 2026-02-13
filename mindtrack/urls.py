from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('analysis/', include('analysis.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('khalti/', include('khalti.urls')),
    path("payments/", include("payments.urls", namespace="payments")),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
