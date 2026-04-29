"""
services/payment/service.py — Razorpay payment service
"""
import os
import hmac
import hashlib
from datetime import datetime, timedelta
import razorpay
from sqlalchemy.orm import Session
from fastapi import HTTPException

from services.payment.models import Plan, Subscription

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

# Initialize razorpay client only if keys are available (avoids crash during local dev without keys)
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    razorpay_client = None

def get_all_plans(db: Session):
    return db.query(Plan).all()

def create_order(db: Session, user_id: str, plan_id: int):
    if not razorpay_client:
        raise HTTPException(status_code=500, detail="Razorpay is not configured")
        
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    amount = plan.price_inr

    order_data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"receipt_{user_id}_{plan_id}",
        "notes": {
            "user_id": user_id,
            "plan_id": plan_id
        }
    }

    try:
        razorpay_order = razorpay_client.order.create(data=order_data)
        
        # Create pending subscription record
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            razorpay_order_id=razorpay_order["id"],
            status="pending"
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return razorpay_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    try:
        msg = f"{order_id}|{payment_id}"
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            msg.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, signature)
    except Exception:
        return False

def activate_subscription(db: Session, order_id: str, payment_id: str, signature: str):
    if not verify_payment_signature(order_id, payment_id, signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    subscription = db.query(Subscription).filter(Subscription.razorpay_order_id == order_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
        
    subscription.razorpay_payment_id = payment_id
    subscription.status = "active"
    subscription.started_at = datetime.utcnow()
    # Provide 30 days of access for this payment
    subscription.expires_at = datetime.utcnow() + timedelta(days=30)
    
    db.commit()
    db.refresh(subscription)
    
    # Update the user's plan
    from services.auth.models import User
    user = db.query(User).filter(User.id == subscription.user_id).first()
    if user:
        user.plan_id = subscription.plan_id
        db.commit()
        
    return subscription

def get_user_subscription(db: Session, user_id: str):
    # Get the latest active subscription
    subscription = db.query(Subscription)\
        .filter(Subscription.user_id == user_id, Subscription.status == "active")\
        .order_by(Subscription.started_at.desc())\
        .first()
    return subscription
