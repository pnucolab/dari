from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dariauth', '0002_server_api_key_nfsshare'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='server_type',
            field=models.CharField(choices=[('compute', 'Compute'), ('storage', 'Storage')], default='compute', max_length=10),
        ),
        migrations.AddField(
            model_name='nfsshare',
            name='allowed_servers',
            field=models.ManyToManyField(blank=True, related_name='accessible_nfs_shares', to='dariauth.server'),
        ),
    ]
