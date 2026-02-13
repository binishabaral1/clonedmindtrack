# payments/views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
import requests
import uuid
from .models import KhaltiPayment

def khalti_initiate(request):
    """
    Initiate a payment request to Khalti
    """
    purchase_order_id = str(uuid.uuid4())
    payload = {
        "return_url": "http://127.0.0.1:8000/payments/khalti/callback/",
        "website_url": "http://127.0.0.1:8000/",
        "amount": 1000,  # paisa (10 NPR)
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

    try:
        response = requests.post(
            "https://dev.khalti.com/api/v2/epayment/initiate/",
            json=payload,
            headers=headers
        )
        data = response.json()
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)})


def khalti_callback(request):
    """
    Callback after payment is done in Khalti.
    Handles:
      1️⃣ Verifying payment
      2️⃣ Preventing duplicate payments
      3️⃣ Upgrading user to premium for 30 days
    """
    pidx = request.GET.get("pidx")
    if not pidx:
        return JsonResponse({"error": "No pidx found"})

    headers = {"Authorization": f"Key {settings.KHALTI_SECRET_KEY}"}
    response = requests.post(
        "https://dev.khalti.com/api/v2/epayment/lookup/",
        json={"pidx": pidx},
        headers=headers
    )
    data = response.json()

    # Check if payment completed
    if response.status_code == 200 and data.get("status") == "Completed":
        # Prevent duplicate payments
        payment, created = KhaltiPayment.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,
            pidx=data["pidx"],
            defaults={
                "transaction_id": data.get("transaction_id", ""),
                "amount": data.get("amount", 0),
                "total_amount": data.get("total_amount", 0),
                "status": data.get("status", ""),
                "fee": data.get("fee", 0),
                "refunded": data.get("refunded", False),
                "purchase_order_id": data.get("purchase_order_id"),
                "purchase_order_name": data.get("purchase_order_name"),
            }
        )

        # Upgrade user to premium for 30 days (Step 1 & 3)
        if request.user.is_authenticated:
            request.user.profile.upgrade_to_premium(days=30)

        return render(request, "payments/khalti_success.html", {"data": data})
    else:
        return render(request, "payments/khalti_failure.html", {"data": data})
