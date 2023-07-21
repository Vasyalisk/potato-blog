# Generated by Django 4.1 on 2023-07-21 10:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("emails", "0003_emailcredentials_created_at_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="unsentemail",
            name="context",
        ),
        migrations.AddField(
            model_name="unsentemail",
            name="html_text",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="unsentemail",
            name="plain_text",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="unsentemail",
            name="subject",
            field=models.CharField(default="", max_length=255),
            preserve_default=False,
        ),
    ]