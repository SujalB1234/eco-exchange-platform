from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # Import inside ready() to avoid AppRegistryNotReady error
        from django.contrib.auth.models import Group
        # Add any logic you want after app is ready
        Group.objects.get_or_create(name='User')
        Group.objects.get_or_create(name='Recycler')
