/**
 * KaNun Monitoring — Stripe Checkout Button Handler
 * 
 * Usage in HTML:
 * <button class="checkout-btn" data-price-id="price_1TtFcKBryn2IZeeRuZhZJJJL">
 *   Subscribe to Solo Monitor
 * </button>
 * 
 * <script src="stripe-checkout.js"></script>
 */

class KaNunCheckout {
  constructor() {
    this.loading = false;
    this.initButtons();
  }

  initButtons() {
    document.querySelectorAll('.checkout-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => this.handleCheckout(e));
    });
  }

  async handleCheckout(event) {
    event.preventDefault();
    
    if (this.loading) return;
    this.loading = true;

    const button = event.target;
    const priceId = button.dataset.priceId;
    const email = document.getElementById('customer-email')?.value;

    if (!priceId) {
      alert('Error: Price ID not found');
      this.loading = false;
      return;
    }

    // Show loading state
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    button.disabled = true;

    try {
      // Call our Netlify function to create checkout session
      const response = await fetch('/.netlify/functions/create-checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          priceId,
          customerEmail: email,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Checkout creation failed');
      }

      const { url } = await response.json();

      // Redirect to Stripe Checkout
      window.location.href = url;
    } catch (error) {
      console.error('Checkout error:', error);
      alert(`Error: ${error.message}`);
      button.textContent = originalText;
      button.disabled = false;
      this.loading = false;
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new KaNunCheckout();
  });
} else {
  new KaNunCheckout();
}
