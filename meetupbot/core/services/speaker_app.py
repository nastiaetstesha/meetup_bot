from decimal import Decimal
from typing import Optional

from django.utils import timezone

from core.models import SpeakerApplication, TelegramUser, Event
from telegram import Update
from telegram.ext import CallbackContext


def create_speaker_app(
    user: TelegramUser,
    event: Optional[Event],
    data: dict
) -> SpeakerApplication:
    try:
        age = int(data["age"].strip()) if "age" in data else None 
        speaker_application = SpeakerApplication.objects.create(
            user=user,
            event=event,
            full_name=data["full_name"].strip(),
            age=age,
            topic_title=data["topic_title"].strip(),
            topic_description=data["topic_description"].strip(), 
            status="new",
        )
        return speaker_application
    except Exception as e:
        raise ValueError(f"Ошибка при создании заявки спикера: {str(e)}")

