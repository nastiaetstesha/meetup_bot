from django.db import models
from django.contrib.auth.models import User


class TelegramUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    tg_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    is_speaker = models.BooleanField(default=False) # пока так примерно
    is_organizer = models.BooleanField(default=False)
    subscribed_to_news = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or str(self.tg_id)


class Event(models.Model):
    '''инфа о мероприятии'''

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Talk(models.Model):
    ''' это отдельный доклад внутри Event '''
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='talks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    speaker = models.ForeignKey(
        TelegramUser, on_delete=models.SET_NULL,
        null=True, related_name='talks',
    )
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_current = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} ({self.event})'


class SpeakerProfile(models.Model):
    ''' Заявка на спикера + биография '''
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    expertise = models.CharField(max_length=255, blank=True)


class SpeakerApplication(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('approved', 'Одобрена'),
        ('rejected', 'Отклонена'),
    ]
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=255)
    age = models.PositiveIntegerField(null=True, blank=True)
    topic_title = models.CharField(max_length=255)
    topic_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)


class FutureEventSubscription(models.Model):
    ''' Запись на следующее мероприятие '''

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)


class NetworkingProfile(models.Model):
    ''' Анкета для нетворкинга '''

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    about = models.TextField()
    experience_level = models.CharField(max_length=50, blank=True)
    tech_stack = models.CharField(max_length=255, blank=True)
    looking_for = models.CharField(max_length=255, blank=True)

    last_filled_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)


class NetworkingEncounter(models.Model):
    ''' История “матчей” и показов анкет для нетворкинга '''

    STATUS_CHOICES = [
        ('shown', 'Показано'),
        ('skipped', 'Пропущен'),
        ('accepted', 'Принят'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    from_user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name='sent_encounters'
    )
    to_user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name='received_encounters'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='shown')
    created_at = models.DateTimeField(auto_now_add=True)


class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    talk = models.ForeignKey(Talk, on_delete=models.SET_NULL, null=True, blank=True)
    author = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    is_answered = models.BooleanField(default=False)
    answered_at = models.DateTimeField(null=True, blank=True)
    answer_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Donation(models.Model):
    ''' Запись о донате.
        не сильно продумана модель, просто для примера.
        Поля (примерно):

        user — кто донатил,
        event — к какому митапу относится донат (или общая поддержка),
        amount, currency — сумма и валюта,
        provider — платёжный провайдер (telegram, yookassa и т.п.),
        provider_payment_id — ID платежа в системе провайдера,
        status — pending/paid/failed,
        даты создания/обновления.'''
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('paid', 'Оплачен'),
        ('failed', 'Ошибка'),
    ]
    user = models.ForeignKey(TelegramUser, on_delete=models.SET_NULL, null=True)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='RUB')
    provider = models.CharField(max_length=50)
    provider_payment_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
