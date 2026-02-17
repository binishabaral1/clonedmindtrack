# analysis/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import MoodAnalysis
import logging

logger = logging.getLogger(__name__)

@login_required
def analyze_mood(request):
    if request.method == "POST":
        text = request.POST.get("text", "").strip()

        if not text:
            return JsonResponse({"success": False, "message": "No text provided"}, status=400)

        try:
            profile = getattr(request.user, 'profile', None)
            if not profile:
                return JsonResponse({"success": False, "message": "User profile not found"}, status=400)

            # Check premium expiry
            if profile.is_premium and profile.premium_until:
                if timezone.now() > profile.premium_until:
                    profile.is_premium = False
                    profile.premium_until = None
                    profile.save()

            # Apply daily limit if not premium
            if not profile.is_premium:
                now = timezone.now()
                start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)

                analyses_today = MoodAnalysis.objects.filter(
                    user=request.user,
                    created_at__gte=start_of_day,
                    created_at__lt=end_of_day
                ).count()

                if analyses_today >= 3:
                    return JsonResponse({
                        "success": False,
                        "message": "Daily limit reached (3 per day). Upgrade to Premium."
                    })

            # Save analysis
            analysis = MoodAnalysis.objects.create(
                user=request.user,
                text=text,
                mood_result="Positive"  # Replace with AI logic later
            )

            return JsonResponse({
                "success": True,
                "mood": analysis.mood_result,
                "premium": profile.is_premium
            })

        except Exception as e:
            logger.exception("Error in analyze_mood view")
            return JsonResponse({"success": False, "message": "Server error occurred"}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request"}, status=400)



