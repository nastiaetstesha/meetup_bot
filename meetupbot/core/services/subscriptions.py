from decimal import Decimal
from typing import Optional

from django.utils import timezone

from core.models import FutureEventSubscription, TelegramUser

def create_subscriptions(
    user: TelegramUser,
    data: dict
) -> FutureEventSubscription:
    try:
        subscriptions = FutureEventSubscription.objects.create(
            user=user,
            comment=data["comment"].strip(),
            is_active= True
        )
        return subscriptions
    except Exception as e:
        raise ValueError(f"Ошибка при создании подписки: {str(e)}")
