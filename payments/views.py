# payments/views.py
from django.http import JsonResponse
from django.conf import settings
import requests
import uuid  # to generate unique purchase_order_id

def khalti_initiate(request):
    try:
        purchase_order_id = str(uuid.uuid4())
        payload = {
            "return_url": "http://127.0.0.1:8000/payments/khalti/callback/",
            "website_url": "http://127.0.0.1:8000/",
            "amount": 1000,  # in paisa
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": "MindTrack Upgrade",
            "customer_info": {
                "name": request.user.username if request.user.is_authenticated else "Test User",
                "email": request.user.email if request.user.is_authenticated else "test@example.com",
                "phone": "9800000000"
            }
        }

        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://dev.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers
        )

        # Log full response for debugging
        print("Khalti response status:", response.status_code)
        print("Khalti response text:", response.text)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"error": "Payment initiation failed", "details": response.text})

    except Exception as e:
        print("Exception in khalti_initiate:", str(e))
        return JsonResponse({"error": str(e)})

def khalti_callback(request):
    """
    Callback after payment is done in Khalti
    """
    pidx = request.GET.get("pidx")
    if not pidx:
        return JsonResponse({"error": "No pidx found"})

    # Verify payment using Khalti Lookup API
    headers = {"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"}
    response = requests.post(
        "https://dev.khalti.com/api/v2/epayment/lookup/",
        json={"pidx": pidx},
        headers=headers
    )
    return JsonResponse(response.json())
