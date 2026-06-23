from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_admin_user(apps, schema_editor):
    Member = apps.get_model('management', 'Member')
    if not Member.objects.filter(username='KCYM@P').exists():
        Member.objects.create(
            username='KCYM@P',
            first_name='KCYM',
            last_name='Pulluvazhy',
            email='kcym.pulluvazhy@gmail.com',
            password=make_password('Pulluvazhy@Admin123'),
            phone_number='9876543210',
            date_of_birth='2000-01-01',
            join_date='2020-01-01',
            blood_group='O+',
            is_active_donor=True,
            role='EXECUTIVE',
            is_staff=True,
            is_superuser=True
        )

def remove_admin_user(apps, schema_editor):
    Member = apps.get_model('management', 'Member')
    Member.objects.filter(username='KCYM@P').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_admin_user, reverse_code=remove_admin_user),
    ]
