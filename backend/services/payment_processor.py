"""
Payment Processing for Hybrid Open Access

Handles article processing charges (APCs) for hybrid OA model.
Integrates with Stripe for payment processing.
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
import stripe

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """
    Handle payments for hybrid open access model.

    Features:
    - Article Processing Charges (APCs)
    - Waivers and discounts
    - Invoice generation
    - Payment tracking
    - Refunds
    - Multi-currency support
    """

    def __init__(self, stripe_api_key: str, currency: str = "USD"):
        """
        Initialize payment processor.

        Args:
            stripe_api_key: Stripe secret API key
            currency: Default currency (USD, EUR, GBP, etc.)
        """
        stripe.api_key = stripe_api_key
        self.currency = currency

    def create_payment_intent(
        self,
        amount: float,
        manuscript_id: str,
        customer_email: str,
        customer_name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a Stripe payment intent for APC.

        Args:
            amount: Amount in dollars/euros/etc
            manuscript_id: Manuscript identifier
            customer_email: Customer email
            customer_name: Customer name
            description: Payment description
            metadata: Additional metadata

        Returns:
            Payment intent details including client_secret
        """
        try:
            # Convert amount to cents
            amount_cents = int(amount * 100)

            # Create or retrieve customer
            customer = self._get_or_create_customer(customer_email, customer_name)

            # Prepare metadata
            payment_metadata = {
                'manuscript_id': manuscript_id,
                'type': 'article_processing_charge',
                **(metadata or {})
            }

            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=self.currency.lower(),
                customer=customer.id,
                description=description or f"APC for manuscript {manuscript_id}",
                metadata=payment_metadata,
                receipt_email=customer_email
            )

            logger.info(f"Created payment intent {intent.id} for manuscript {manuscript_id}")

            return {
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'amount': amount,
                'currency': self.currency,
                'status': intent.status,
                'customer_id': customer.id
            }

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return {
                'error': str(e),
                'type': type(e).__name__
            }

    def confirm_payment(self, payment_intent_id: str) -> Dict:
        """
        Confirm a payment intent.

        Args:
            payment_intent_id: Payment intent ID

        Returns:
            Payment confirmation details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            return {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'amount_received': intent.amount_received / 100,
                'currency': intent.currency.upper(),
                'paid': intent.status == 'succeeded',
                'metadata': intent.metadata
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return {'error': str(e)}

    def create_invoice(
        self,
        customer_email: str,
        customer_name: str,
        line_items: List[Dict],
        manuscript_id: str,
        due_days: int = 30
    ) -> Dict:
        """
        Create an invoice for APC.

        Args:
            customer_email: Customer email
            customer_name: Customer name
            line_items: List of invoice line items
            manuscript_id: Manuscript identifier
            due_days: Days until due

        Returns:
            Invoice details
        """
        try:
            # Get or create customer
            customer = self._get_or_create_customer(customer_email, customer_name)

            # Create invoice items
            for item in line_items:
                stripe.InvoiceItem.create(
                    customer=customer.id,
                    amount=int(item['amount'] * 100),
                    currency=self.currency.lower(),
                    description=item['description']
                )

            # Create invoice
            invoice = stripe.Invoice.create(
                customer=customer.id,
                auto_advance=True,
                collection_method='send_invoice',
                days_until_due=due_days,
                metadata={'manuscript_id': manuscript_id}
            )

            # Finalize and send
            invoice = stripe.Invoice.finalize_invoice(invoice.id)

            logger.info(f"Created invoice {invoice.id} for manuscript {manuscript_id}")

            return {
                'invoice_id': invoice.id,
                'invoice_number': invoice.number,
                'amount_due': invoice.amount_due / 100,
                'currency': invoice.currency.upper(),
                'status': invoice.status,
                'invoice_pdf': invoice.invoice_pdf,
                'hosted_invoice_url': invoice.hosted_invoice_url
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error creating invoice: {str(e)}")
            return {'error': str(e)}

    def apply_waiver(
        self,
        manuscript_id: int,
        waiver_type: str,
        waiver_percentage: int,
        reason: str,
        approved_by_id: int,
        db_session
    ) -> 'PaymentWaiver':
        """
        Apply APC waiver for a manuscript.

        Args:
            manuscript_id: Manuscript database ID
            waiver_type: Type of waiver (full, partial, institutional)
            waiver_percentage: Percentage to waive (0-100)
            reason: Reason for waiver
            approved_by_id: User ID of approver
            db_session: Database session

        Returns:
            PaymentWaiver object
        """
        from db.models import PaymentWaiver

        waiver = PaymentWaiver(
            manuscript_id=manuscript_id,
            waiver_type=waiver_type,
            waiver_percentage=waiver_percentage,
            reason=reason,
            approved_by_id=approved_by_id,
            approved_at=datetime.utcnow()
        )

        db_session.add(waiver)
        db_session.commit()
        db_session.refresh(waiver)

        logger.info(f"Applied {waiver_percentage}% waiver to manuscript {manuscript_id}")

        return waiver

    def process_refund(
        self,
        payment_intent_id: str,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Dict:
        """
        Process a refund for a payment.

        Args:
            payment_intent_id: Payment intent ID to refund
            amount: Amount to refund (None for full refund)
            reason: Reason for refund

        Returns:
            Refund details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            refund_data = {'payment_intent': payment_intent_id}

            if amount:
                refund_data['amount'] = int(amount * 100)

            if reason:
                refund_data['reason'] = reason

            refund = stripe.Refund.create(**refund_data)

            logger.info(f"Processed refund {refund.id} for payment intent {payment_intent_id}")

            return {
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'currency': refund.currency.upper(),
                'status': refund.status,
                'reason': refund.reason
            }

        except stripe.error.StripeError as e:
            logger.error(f"Error processing refund: {str(e)}")
            return {'error': str(e)}

    def get_payment_history(
        self,
        customer_email: Optional[str] = None,
        manuscript_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get payment history for a customer or manuscript.

        Args:
            customer_email: Customer email (optional)
            manuscript_id: Manuscript ID (optional)
            limit: Maximum number of records

        Returns:
            List of payment records
        """
        try:
            params = {'limit': limit}

            if customer_email:
                customer = self._find_customer(customer_email)
                if customer:
                    params['customer'] = customer.id

            payment_intents = stripe.PaymentIntent.list(**params)

            history = []
            for intent in payment_intents.auto_paging_iter():
                # Filter by manuscript_id if specified
                if manuscript_id and intent.metadata.get('manuscript_id') != manuscript_id:
                    continue

                history.append({
                    'payment_intent_id': intent.id,
                    'amount': intent.amount / 100,
                    'currency': intent.currency.upper(),
                    'status': intent.status,
                    'created': datetime.fromtimestamp(intent.created).isoformat(),
                    'manuscript_id': intent.metadata.get('manuscript_id'),
                    'customer_email': intent.receipt_email
                })

            return history

        except stripe.error.StripeError as e:
            logger.error(f"Error retrieving payment history: {str(e)}")
            return []

    def calculate_apc(
        self,
        base_price: float,
        manuscript_id: int,
        db_session
    ) -> Dict:
        """
        Calculate APC after applying waivers and discounts.

        Args:
            base_price: Base APC amount
            manuscript_id: Manuscript database ID
            db_session: Database session

        Returns:
            APC calculation breakdown
        """
        from db.models import PaymentWaiver

        # Check for waivers
        waiver = db_session.query(PaymentWaiver).filter(
            PaymentWaiver.manuscript_id == manuscript_id
        ).first()

        if waiver:
            discount = (base_price * waiver.waiver_percentage) / 100
            final_price = base_price - discount

            return {
                'base_price': base_price,
                'waiver_percentage': waiver.waiver_percentage,
                'waiver_amount': discount,
                'final_price': final_price,
                'waiver_reason': waiver.reason,
                'currency': self.currency
            }
        else:
            return {
                'base_price': base_price,
                'waiver_percentage': 0,
                'waiver_amount': 0,
                'final_price': base_price,
                'currency': self.currency
            }

    def _get_or_create_customer(self, email: str, name: str) -> 'stripe.Customer':
        """Get existing customer or create new one."""
        customer = self._find_customer(email)

        if customer:
            return customer

        # Create new customer
        customer = stripe.Customer.create(
            email=email,
            name=name,
            description=f"Journal author: {name}"
        )

        return customer

    def _find_customer(self, email: str) -> Optional['stripe.Customer']:
        """Find customer by email."""
        try:
            customers = stripe.Customer.list(email=email, limit=1)
            if customers.data:
                return customers.data[0]
        except stripe.error.StripeError as e:
            logger.error(f"Error finding customer: {str(e)}")

        return None


# Pricing tiers for different article types
PRICING_TIERS = {
    'research_article': 2500.00,  # USD
    'review_article': 3000.00,
    'case_study': 1500.00,
    'short_communication': 1000.00,
    'letter': 800.00,
    'editorial': 0.00,  # No charge for editorials
    'correction': 0.00
}


def create_payment_for_manuscript(
    manuscript_id: int,
    db_session,
    stripe_api_key: str
) -> Dict:
    """
    Create payment intent for a manuscript's APC.

    Args:
        manuscript_id: Manuscript database ID
        db_session: Database session
        stripe_api_key: Stripe API key

    Returns:
        Payment intent details
    """
    from db.models import Manuscript

    manuscript = db_session.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise ValueError(f"Manuscript {manuscript_id} not found")

    # Get base price based on article type
    base_price = PRICING_TIERS.get(manuscript.article_type, PRICING_TIERS['research_article'])

    # Initialize payment processor
    processor = PaymentProcessor(stripe_api_key)

    # Calculate final price with waivers
    pricing = processor.calculate_apc(base_price, manuscript_id, db_session)

    if pricing['final_price'] == 0:
        # No payment required
        return {
            'payment_required': False,
            'message': 'No payment required for this article type or full waiver applied',
            'pricing': pricing
        }

    # Get corresponding author
    corresponding_author = manuscript.authors[0] if manuscript.authors else None

    if not corresponding_author:
        raise ValueError("No author found for manuscript")

    # Create payment intent
    intent = processor.create_payment_intent(
        amount=pricing['final_price'],
        manuscript_id=manuscript.manuscript_id,
        customer_email=corresponding_author.email,
        customer_name=corresponding_author.full_name,
        description=f"Article Processing Charge - {manuscript.title[:50]}",
        metadata={
            'article_type': manuscript.article_type,
            'waiver_applied': pricing['waiver_percentage'] > 0
        }
    )

    return {
        'payment_required': True,
        'pricing': pricing,
        'payment_intent': intent
    }


"""
Add to db/models.py:

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False)
    payment_intent_id = Column(String(255), unique=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default='USD')
    status = Column(String(50))  # pending, succeeded, failed, refunded
    payment_method = Column(String(50))  # card, bank_transfer, etc.
    transaction_id = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    paid_at = Column(DateTime(timezone=True))
    refunded_at = Column(DateTime(timezone=True))

    # Relationships
    manuscript = relationship("Manuscript", back_populates="payments")


class PaymentWaiver(Base):
    __tablename__ = "payment_waivers"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False)
    waiver_type = Column(String(50))  # full, partial, institutional
    waiver_percentage = Column(Integer)  # 0-100
    reason = Column(Text)
    approved_by_id = Column(Integer, ForeignKey('users.id'))
    approved_at = Column(DateTime(timezone=True))

    # Relationships
    manuscript = relationship("Manuscript")
    approved_by = relationship("User")
"""
