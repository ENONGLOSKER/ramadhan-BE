# Generated by Django 5.1.6 on 2025-03-01 14:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_rc', '0002_remove_jadwalsalat_lokasi'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MisiRamadan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal', models.DateField()),
                ('deskripsi', models.TextField()),
                ('selesai', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PencapaianPengguna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('selesai_pada', models.DateTimeField(auto_now_add=True)),
                ('misi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_rc.misiramadan')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
