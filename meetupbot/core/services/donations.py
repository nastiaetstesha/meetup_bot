from decimal import Decimal
from typing import Optional

from django.utils import timezone

from core.models import Donation, TelegramUser, Event

# Сервис для работы с донатами - FAKE-версия, для примера.

def create_pending_donation(
    user: TelegramUser,
    event: Optional[Event],
    amount: Decimal,
    provider: str = "fake",
) -> Donation:
    return Donation.objects.create(
        user=user,
        event=event,
        amount=amount,
        currency="RUB",
        provider=provider,
        status="pending",
    )


def mark_donation_paid(donation: Donation, provider_payment_id: str | None = None) -> Donation:
    donation.status = "paid"
    if provider_payment_id:
        donation.provider_payment_id = provider_payment_id
    donation.updated_at = timezone.now()
    donation.save()
    return donation
