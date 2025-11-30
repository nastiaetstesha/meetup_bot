from django.contrib import admin
from .models import (
    TelegramUser, Event, Talk,
    SpeakerProfile, SpeakerApplication,
    FutureEventSubscription,
    NetworkingProfile,
    Question, Donation,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'is_current', 'is_active')
    list_filter = ('is_active', 'is_current')


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'speaker', 'order', 'is_current')
    list_filter = ('event',)

@admin.register(NetworkingProfile)
class NetworkingProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'stack', 'goal')


admin.site.register(TelegramUser)
admin.site.register(SpeakerProfile)
admin.site.register(SpeakerApplication)
admin.site.register(FutureEventSubscription)
admin.site.register(Question)
admin.site.register(Donation)
