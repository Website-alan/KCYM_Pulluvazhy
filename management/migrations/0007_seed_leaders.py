from django.db import migrations
from django.contrib.auth.hashers import make_password

def seed_leaders(apps, schema_editor):
    Member = apps.get_model('management', 'Member')
    default_password = make_password('Pulluvazhy@Admin123')
    
    # Vicar
    if not Member.objects.filter(username='fr_thomas').exists():
        Member.objects.create(
            username='fr_thomas',
            first_name='Fr. Thomas',
            last_name='Pulluvazhy',
            email='vicar.stthomas@gmail.com',
            password=default_password,
            phone_number='9876543221',
            date_of_birth='1970-01-01',
            join_date='2018-05-15',
            blood_group='O+',
            is_active_donor=True,
            role='VICAR',
            is_active=True
        )
        
    # Assistant Vicar
    if not Member.objects.filter(username='fr_joseph').exists():
        Member.objects.create(
            username='fr_joseph',
            first_name='Fr. Joseph',
            last_name='Assistant',
            email='assistant.stthomas@gmail.com',
            password=default_password,
            phone_number='9876543222',
            date_of_birth='1985-01-01',
            join_date='2022-05-15',
            blood_group='A+',
            is_active_donor=True,
            role='ASSISTANT_VICAR',
            is_active=True
        )

    # President
    if not Member.objects.filter(username='albin_benny').exists():
        Member.objects.create(
            username='albin_benny',
            first_name='Albin',
            last_name='Benny',
            email='albin.kcym@gmail.com',
            password=default_password,
            phone_number='9876543223',
            date_of_birth='2000-01-01',
            join_date='2020-01-01',
            blood_group='B+',
            is_active_donor=True,
            role='EXECUTIVE',
            is_active=True
        )

    # Secretary
    if not Member.objects.filter(username='anjali_kurian').exists():
        Member.objects.create(
            username='anjali_kurian',
            first_name='Anjali',
            last_name='Kurian',
            email='anjali.kcym@gmail.com',
            password=default_password,
            phone_number='9876543224',
            date_of_birth='2001-01-01',
            join_date='2020-01-01',
            blood_group='AB+',
            is_active_donor=True,
            role='EXECUTIVE',
            is_active=True
        )

def remove_leaders(apps, schema_editor):
    Member = apps.get_model('management', 'Member')
    Member.objects.filter(username__in=['fr_thomas', 'fr_joseph', 'albin_benny', 'anjali_kurian']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('management', '0006_member_profile_image'),
    ]

    operations = [
        migrations.RunPython(seed_leaders, reverse_code=remove_leaders),
    ]
