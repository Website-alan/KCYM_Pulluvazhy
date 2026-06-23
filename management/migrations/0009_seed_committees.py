from django.db import migrations

def seed_committee_data(apps, schema_editor):
    Member = apps.get_model('management', 'Member')
    Committee = apps.get_model('management', 'Committee')
    CommitteeMember = apps.get_model('management', 'CommitteeMember')
    
    # Create Committee
    committee, created = Committee.objects.get_or_create(
        name="2025 - 26 KCYM Committee",
        defaults={
            'start_year': 2025,
            'end_year': 2026,
            'is_active': True
        }
    )
    
    # Link President
    albin = Member.objects.filter(username='albin_benny').first()
    if albin and not CommitteeMember.objects.filter(committee=committee, member=albin).exists():
        CommitteeMember.objects.create(
            committee=committee,
            member=albin,
            position='PRESIDENT'
        )
        
    # Link Secretary
    anjali = Member.objects.filter(username='anjali_kurian').first()
    if anjali and not CommitteeMember.objects.filter(committee=committee, member=anjali).exists():
        CommitteeMember.objects.create(
            committee=committee,
            member=anjali,
            position='SECRETARY'
        )

def remove_committee_data(apps, schema_editor):
    Committee = apps.get_model('management', 'Committee')
    Committee.objects.filter(name="2025 - 26 KCYM Committee").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('management', '0008_committee_alter_member_role_committeemember'),
    ]

    operations = [
        migrations.RunPython(seed_committee_data, reverse_code=remove_committee_data),
    ]
