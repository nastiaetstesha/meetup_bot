from core.models import TelegramUser, NetworkingProfile


def get_or_create_telegram_user(tg_user):
    obj, _ = TelegramUser.objects.get_or_create(
        tg_id=tg_user.id,
        defaults={
            "username": tg_user.username or "",
            "first_name": tg_user.first_name or "",
            "last_name": tg_user.last_name or "",
        }
    )
    return obj


def save_profile(tg_user, profile_data: dict):
    user = get_or_create_telegram_user(tg_user)

    profile, _ = NetworkingProfile.objects.update_or_create(
        user=user,
        defaults={
            "name": profile_data["name"],
            "age": profile_data["age"],
            "stack": profile_data["stack"],
            "goal": profile_data["goal"],
        }
    )
    return profile


def get_saved_profile(tg_user):
    try:
        user = TelegramUser.objects.get(tg_id=tg_user.id)
    except TelegramUser.DoesNotExist:
        return None

    return getattr(user, "networking_profile", None)
