from core.models import NetworkingProfile

def get_other_profiles(current_user_tg_id):
    return list(
        NetworkingProfile.objects
        .exclude(user__tg_id=current_user_tg_id)
        .order_by("-updated_at")
    )