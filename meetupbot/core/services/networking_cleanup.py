from core.models import NetworkingProfile

def clear_networking_profiles():
    NetworkingProfile.objects.all().delete()