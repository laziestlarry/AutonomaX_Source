'use client';
import { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { ShoppingCart, Loader2 } from 'lucide-react';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export default function CheckoutButton({ packId, priceId, label }: { packId: string, priceId: string, label: string }) {
  const [loading, setLoading] = useState(false);

  const handleCheckout = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ priceId, packId }),
      });
      const { sessionId } = await response.json();
      const stripe = await stripePromise;
      await stripe?.redirectToCheckout({ sessionId });
    } catch (error) {
      console.error("Checkout failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button 
      onClick={handleCheckout} 
      disabled={loading}
      className="flex items-center justify-center gap-2 bg-kagan-accent text-kagan-dark px-6 py-3 rounded-xl font-bold hover:scale-105 transition-transform"
    >
      {loading ? <Loader2 className="animate-spin" /> : <ShoppingCart />}
      {label}
    </button>
  );
}