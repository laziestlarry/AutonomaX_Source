from fastapi import FastAPI, Request, HTTPException
import stripe
import os
from celery_worker import execute_golden_delivery # Your internal job queue

app = FastAPI(title="AutonomaX Mission Director")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        pack_id = session["metadata"]["packId"]
        
        # Enqueue the autonomous fulfillment bot
        execute_golden_delivery.delay(
            email=customer_email,
            pack_type=pack_id,
            action="PROVISION_WORKSPACE_AND_SEND_WELCOME"
        )
        
        # Log to Profit OS BigQuery
        log_to_profit_os(session["amount_total"], pack_id, customer_email)

    return {"status": "success"}