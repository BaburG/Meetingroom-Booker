# Generated by Django 5.0.7 on 2024-08-02 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booker_engine', '0003_booking_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='userid',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
