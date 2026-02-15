from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from analysis.models import MoodAnalysis


def home_view(request):
    """Home page view"""
    return render(request, 'home.html')


@login_required
def dashboard_view(request):
    """Dashboard view for logged in users"""

    profile = request.user.profile

    # ✅ Check premium expiry
    if profile.is_premium and profile.premium_until:
        if timezone.now() > profile.premium_until:
            profile.is_premium = False
            profile.premium_until = None
            profile.save()

    # ✅ Today's date range
    now = timezone.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    # ✅ Count today's analyses
    analyses_count_today = MoodAnalysis.objects.filter(
        user=request.user,
        created_at__gte=start_of_day,
        created_at__lt=end_of_day
    ).count()

    # ✅ Free remaining logic
    if profile.is_premium:
        free_remaining = "Unlimited"
        is_locked = False
    else:
        free_remaining = max(0, 3 - analyses_count_today)
        is_locked = analyses_count_today >= 3

    # ✅ Last 5 analyses (overall)
    recent_analyses = MoodAnalysis.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    return render(request, 'dashboard/index.html', {
        'user': request.user,
        'free_analyses_remaining': free_remaining,
        'analysis_history': recent_analyses,
        'is_locked': is_locked,
        'is_premium': profile.is_premium,  # ✅ new
    })
