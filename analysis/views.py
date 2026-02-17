from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import MoodAnalysis
import logging

logger = logging.getLogger(__name__)

@login_required
def analyze_mood(request):

    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

    text = request.POST.get("text", "").strip()

    if not text:
        return JsonResponse({"success": False, "message": "No text provided"}, status=400)

    try:
        profile = request.user.profile

        # ==============================
        # ✅ Check Premium Expiry
        # ==============================
        if profile.is_premium and profile.premium_until:
            if timezone.now() > profile.premium_until:
                profile.is_premium = False
                profile.premium_until = None
                profile.save()

        # ==============================
        # ✅ Daily Limit Logic
        # ==============================
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        analyses_today = MoodAnalysis.objects.filter(
            user=request.user,
            created_at__gte=start_of_day,
            created_at__lt=end_of_day
        ).count()

        if not profile.is_premium:
            if analyses_today >= 3:
                return JsonResponse({
                    "success": False,
                    "message": "Daily limit reached (3 per day). Upgrade to Premium.",
                    "premium": False,
                    "free_remaining": 0
                })

            free_remaining = 3 - (analyses_today + 1)
        else:
            free_remaining = None  # Unlimited

        # ==============================
        # ✅ Mood Detection Logic
        # ==============================
        text_lower = text.lower()

        mood_keywords = {
            'happy': ['happy', 'joy', 'good', 'great', 'wonderful', 'excited', 'love', 'amazing'],
            'sad': ['sad', 'unhappy', 'depressed', 'cry', 'tears', 'lonely'],
            'angry': ['angry', 'mad', 'hate', 'annoyed', 'furious'],
            'fear': ['fear', 'scared', 'afraid', 'anxious', 'worried'],
            'neutral': ['okay', 'fine', 'normal', 'alright'],
            'surprise': ['surprise', 'wow', 'shocked', 'unexpected']
        }

        scores = {mood: 0 for mood in mood_keywords}

        for mood, keywords in mood_keywords.items():
            for word in keywords:
                if word in text_lower:
                    scores[mood] += 1

        total_score = sum(scores.values())

        if total_score > 0:
            detected_mood = max(scores, key=scores.get)
            emotions = {k: v / total_score for k, v in scores.items()}
            confidence = emotions[detected_mood]
        else:
            detected_mood = "neutral"
            emotions = {
                'happy': 0.2,
                'sad': 0.2,
                'angry': 0.1,
                'fear': 0.1,
                'neutral': 0.3,
                'surprise': 0.1
            }
            confidence = 0.5

        # ==============================
        # ✅ Save to Database
        # ==============================
        MoodAnalysis.objects.create(
            user=request.user,
            text=text,
            detected_mood=detected_mood,
            confidence=confidence,
            emotions=emotions
        )

        # ==============================
        # ✅ Return JSON
        # ==============================
        return JsonResponse({
            "success": True,
            "mood": detected_mood,
            "confidence": f"{round(confidence * 100)}%",
            "emotions": {k: f"{round(v * 100, 1)}%" for k, v in emotions.items()},
            "premium": profile.is_premium,
            "free_remaining": free_remaining
        })

    except Exception as e:
        logger.exception("Error in analyze_mood view")
        return JsonResponse({
            "success": False,
            "message": "Server error occurred"
        }, status=500)
