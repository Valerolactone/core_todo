# Generated by Django 5.0.7 on 2024-07-29 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "api",
            "0004_rename_participation_pk_projectparticipant_project_participant_pk_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="deadline_notified",
            field=models.BooleanField(default=False),
        ),
    ]
