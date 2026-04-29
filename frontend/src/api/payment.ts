import { BASE_URL } from "./auth";
import { getAuthHeaders } from "./agent";

export interface Plan {
  id: number;
  name: string;
  price_inr: number;
  max_contacts: number;
  max_emails: number;
  max_campaigns: number;
}

export async function fetchPlans(): Promise<Plan[]> {
  const res = await fetch(`${BASE_URL}/payment/plans`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch plans");
  return res.json();
}

export async function createOrder(planId: number): Promise<{ order_id: string; amount: number; currency: string }> {
  const res = await fetch(`${BASE_URL}/payment/create-order`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ plan_id: planId })
  });
  if (!res.ok) throw new Error("Failed to create order");
  return res.json();
}

export async function verifyPayment(orderId: string, paymentId: string, signature: string) {
  const res = await fetch(`${BASE_URL}/payment/verify`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({
      razorpay_order_id: orderId,
      razorpay_payment_id: paymentId,
      razorpay_signature: signature
    })
  });
  if (!res.ok) throw new Error("Failed to verify payment");
  return res.json();
}

export async function fetchSubscription() {
  const res = await fetch(`${BASE_URL}/payment/subscription`, { headers: getAuthHeaders() });
  if (!res.ok) throw new Error("Failed to fetch subscription");
  return res.json();
}
