# analysis/urls.py
# from django.urls import path
# from . import views
# from .views import analyze_mood

# urlpatterns = [
#     path('analyze/', views.analyze_text_view, name='analyze_text'),
#     path('analyze-ajax/', views.analyze_text_ajax, name='analyze_ajax'),
#     path('history/', views.history_view, name='history'),
#      path('analyze/', views.analyze_mood, name='analyze_mood'),
# ]
# analysis/urls.py
from django.urls import path
from .views import analyze_mood

urlpatterns = [
    path('analyze/', analyze_mood, name='analyze_mood'),
]

