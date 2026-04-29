"""
services/payment/router.py — FastAPI router for payment endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from services.auth.dependencies import get_db, get_current_user
from services.auth.models import User
from services.payment import service

router = APIRouter(prefix="/payment", tags=["payment"])

class OrderRequest(BaseModel):
    plan_id: int

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

@router.get("/plans")
def list_plans(db: Session = Depends(get_db)):
    return service.get_all_plans(db)

@router.post("/create-order")
def create_order(request: OrderRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.create_order(db, current_user.id, request.plan_id)

@router.post("/verify")
def verify_payment(verification: PaymentVerification, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.activate_subscription(
        db, 
        verification.razorpay_order_id, 
        verification.razorpay_payment_id, 
        verification.razorpay_signature
    )

@router.get("/subscription")
def get_subscription(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    subscription = service.get_user_subscription(db, current_user.id)
    if not subscription:
        return {"has_active_subscription": False}
    
    plan = db.query(service.Plan).filter(service.Plan.id == subscription.plan_id).first()
    
    return {
        "has_active_subscription": True,
        "subscription_id": subscription.id,
        "plan": {
            "id": plan.id,
            "name": plan.name,
            "max_contacts": plan.max_contacts,
            "max_emails": plan.max_emails,
            "max_campaigns": plan.max_campaigns
        },
        "started_at": subscription.started_at,
        "expires_at": subscription.expires_at
    }

@router.post("/webhook")
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook for asynchronous payment verification."""
    # Read the body and signature
    # Since this is a test environment setup mostly, we'll keep it simple
    # The actual implementation would verify the webhook signature here
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature")
    
    # In production, verify the signature using razorpay_client.utility.verify_webhook_signature
    
    # Process event
    # payload = await request.json()
    # event = payload.get("event")
    # ... handle 'payment.captured' etc
    
    return {"status": "ok"}
