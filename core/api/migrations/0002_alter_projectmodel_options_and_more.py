# Generated by Django 5.0.7 on 2024-07-22 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="projectmodel",
            options={"ordering": ["-created_at"]},
        ),
        migrations.RenameField(
            model_name="projectparticipantsmodel",
            old_name="project_id",
            new_name="project",
        ),
        migrations.RenameField(
            model_name="tasksattachmentsmodel",
            old_name="task_id",
            new_name="task",
        ),
        migrations.RenameField(
            model_name="tasksubscribersmodel",
            old_name="task_id",
            new_name="task",
        ),
        migrations.RemoveField(
            model_name="projectmodel",
            name="logo",
        ),
        migrations.RemoveField(
            model_name="tasksattachmentsmodel",
            name="attachment",
        ),
        migrations.AddField(
            model_name="projectmodel",
            name="logo_id",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tasksattachmentsmodel",
            name="attachment_id",
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
