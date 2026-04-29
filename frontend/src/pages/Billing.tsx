import { useState, useEffect } from "react";
import { CreditCard, Check, Zap, Loader2 } from "lucide-react";
import { fetchPlans, createOrder, verifyPayment, fetchSubscription, type Plan } from "../api/payment";

export default function Billing() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [subscription, setSubscription] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<number | null>(null);

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
    // Load Razorpay Script dynamically
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);
    return () => { document.body.removeChild(script); };
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const p = await fetchPlans();
      setPlans(p);
    } catch (e: any) {
      console.error(e);
      setError("Failed to load plans. Is the backend running?");
    }
    
    try {
      const s = await fetchSubscription();
      setSubscription(s);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleSubscribe = async (plan: Plan) => {
    try {
      setProcessingId(plan.id);
      
      // 1. Create Order on Backend
      const order = await createOrder(plan.id);

      // 2. Open Razorpay Checkout Modal
      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID || "", // Will fail gracefully if missing
        amount: order.amount,
        currency: order.currency,
        name: "PersonaFlow",
        description: `${plan.name} Subscription`,
        order_id: order.order_id,
        handler: async function (response: any) {
          // 3. Verify Payment on Backend
          try {
            await verifyPayment(response.razorpay_order_id, response.razorpay_payment_id, response.razorpay_signature);
            alert("Payment Successful! Your subscription is active.");
            loadData();
          } catch (e) {
            alert("Payment verification failed.");
          }
        },
        prefill: {
          name: "User",
          email: "user@example.com",
        },
        theme: {
          color: "#7c3aed" // Electric Violet
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on('payment.failed', function (response: any) {
        alert(`Payment failed: ${response.error.description}`);
      });
      rzp.open();

    } catch (e: any) {
      alert("Error initiating checkout: " + e.message);
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return <div className="h-full flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-brand-500" /></div>;
  }

  return (
    <div className="max-w-5xl mx-auto py-8">
      <div className="mb-8">
        <h2 className="page-title">Billing & Plans</h2>
        <p className="page-subtitle">Manage your subscription and upgrade your outreach limits.</p>
      </div>

      {error && (
        <div className="p-4 mb-8 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
          {error}
        </div>
      )}

      {subscription?.has_active_subscription && (
        <div className="glass-card p-6 mb-10 flex items-center justify-between border-brand-500/30 bg-brand-900/10">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-brand-500/20 rounded-full flex items-center justify-center">
              <Zap className="w-6 h-6 text-brand-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-100">Current Plan: {subscription.plan.name}</h3>
              <p className="text-sm text-slate-400">
                Limits: {subscription.plan.max_emails} Emails | {subscription.plan.max_campaigns} Campaigns | {subscription.plan.max_contacts} Contacts
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">Renews on</div>
            <div className="font-medium text-slate-200">
              {new Date(subscription.expires_at).toLocaleDateString()}
            </div>
          </div>
        </div>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const isCurrent = subscription?.has_active_subscription && subscription.plan.id === plan.id;
          return (
            <div key={plan.id} className={`glass-card p-6 flex flex-col relative ${plan.name === 'Premium' ? 'border-brand-500 shadow-glow-brand' : ''}`}>
              {plan.name === 'Premium' && (
                <div className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2 bg-brand-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                  RECOMMENDED
                </div>
              )}
              
              <h3 className="text-xl font-semibold text-slate-100">{plan.name}</h3>
              <div className="mt-4 mb-6">
                <span className="text-3xl font-bold">₹{plan.price_inr}</span>
                <span className="text-slate-400 text-sm"> / month</span>
              </div>
              
              <ul className="space-y-3 mb-8 flex-1">
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-emerald-400" />
                  {plan.max_contacts} Contacts
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-emerald-400" />
                  {plan.max_emails} Emails / mo
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-emerald-400" />
                  {plan.max_campaigns} Campaigns
                </li>
              </ul>

              <button
                disabled={isCurrent || processingId === plan.id}
                onClick={() => handleSubscribe(plan)}
                className={`w-full justify-center ${isCurrent ? 'btn-secondary opacity-50 cursor-not-allowed' : plan.name === 'Premium' ? 'btn-primary' : 'btn-secondary'}`}
              >
                {processingId === plan.id ? <Loader2 className="w-4 h-4 animate-spin" /> : 
                 isCurrent ? "Current Plan" : "Subscribe via UPI"}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
