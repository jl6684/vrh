from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile objects for users who do not have them'

    def handle(self, *args, **options):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created profile for user: {user.username}')
            )
        
        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('All users already have profiles.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} user profiles.')
            )
