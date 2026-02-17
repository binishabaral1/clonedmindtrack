# analysis/services.py
import requests
import json
from django.conf import settings

class MoodAnalyzer:
    """Analyze mood using Hugging Face DistilBERT API"""
    
    # Free model from Hugging Face
    API_URL = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
    
    # For demo/testing (no API key needed)
    EMOTION_MAP = {
        'anger': 'angry',
        'disgust': 'angry',  # Map to angry
        'fear': 'fear',
        'joy': 'happy',
        'neutral': 'neutral',
        'sadness': 'sad',
        'surprise': 'surprise'
    }
    
    @staticmethod
    def analyze_text_simulated(text):
        """
        Simulated mood analysis for development
        Returns consistent results based on keywords
        """
        text_lower = text.lower()
        
        # Keyword-based detection (simple fallback)
        mood_keywords = {
            'happy': ['happy', 'joy', 'good', 'great', 'wonderful', 'excited', 'love', 'amazing'],
            'sad': ['sad', 'unhappy', 'depressed', 'cry', 'tears', 'lonely', 'miserable'],
            'angry': ['angry', 'mad', 'hate', 'annoyed', 'furious', 'rage', 'angry'],
            'fear': ['fear', 'scared', 'afraid', 'anxious', 'worried', 'nervous', 'panic'],
            'neutral': ['okay', 'fine', 'normal', 'alright', 'meh', 'whatever'],
            'surprise': ['surprise', 'wow', 'shocked', 'unexpected', 'amazing']
        }
        
        # Count keyword matches
        scores = {mood: 0 for mood in mood_keywords}
        
        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[mood] += 1
        
        # Add intensity
        intensity_words = ['very', 'really', 'extremely', 'so', 'super']
        words = text_lower.split()
        for i, word in enumerate(words):
            if word in intensity_words and i + 1 < len(words):
                next_word = words[i + 1]
                for mood, keywords in mood_keywords.items():
                    if next_word in keywords:
                        scores[mood] += 2
        
        # If no matches, default to neutral
        if all(score == 0 for score in scores.values()):
            return {
                'detected_mood': 'neutral',
                'confidence': 0.5,
                'emotions': {
                    'happy': 0.1,
                    'sad': 0.1,
                    'angry': 0.1,
                    'fear': 0.1,
                    'neutral': 0.5,
                    'surprise': 0.1
                }
            }
        
        # Find dominant mood
        total_score = sum(scores.values())

if total_score > 0:
    detected_mood = max(scores, key=scores.get)
    emotions = {k: v / total_score for k, v in scores.items()}

    # ✅ Improved confidence logic
    confidence = (scores[detected_mood] / total_score) * (min(total_score, 3) / 3)

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

    @staticmethod
    def analyze_text_api(text, api_key=None):
        """
        Real Hugging Face API call
        Comment: We'll implement this later when we get API key
        """
        # For now, use simulated version
        return MoodAnalyzer.analyze_text_simulated(text)

def analyze_mood(text, user):
    """Main function to analyze mood and save result"""
    analyzer = MoodAnalyzer()
    
    # Use simulated analysis for now
    result = analyzer.analyze_text_simulated(text)
    
    # Save to database
    from .models import MoodAnalysis
    
    mood_entry = MoodAnalysis.objects.create(
        user=user,
        text=text,
        detected_mood=result['detected_mood'],
        confidence=result['confidence'],
        emotions=result['emotions']
    )
    
    return mood_entry