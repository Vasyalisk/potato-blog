# Generated by Django 4.1 on 2023-07-21 11:33

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0005_unsentemail_reason"),
    ]

    operations = [
        migrations.RenameField(
            model_name="emailcredentials",
            old_name="use_SSL",
            new_name="use_ssl",
        ),
        migrations.RenameField(
            model_name="emailcredentials",
            old_name="use_TSL",
            new_name="use_tsl",
        ),
    ]
