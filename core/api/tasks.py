import smtplib
from datetime import datetime, timedelta

from api.models import Task, TaskSubscriber
from celery import shared_task

from core.settings import lazy_settings


# TODO: решить вопрос с имейлами
@shared_task
def send_task_deadline_notification():
    now = datetime.utcnow()
    one_hour_from_now = now + timedelta(hours=1)
    tasks_due_soon = Task.objects.filter(
        due_date__lte=one_hour_from_now, deadline_notified=False
    )
    for task in tasks_due_soon:
        task_subscribers = TaskSubscriber.object.filter(task=task)
        try:
            with smtplib.SMTP(
                lazy_settings.EMAIL_HOST, lazy_settings.EMAIL_PORT
            ) as server:
                server.starttls()
                server.login(
                    lazy_settings.EMAIL_HOST_USER, lazy_settings.EMAIL_HOST_PASSWORD
                )
                msg = f"There's an hour left until the deadline for task {task.title}."
                for subscriber in task_subscribers:
                    server.sendmail(
                        lazy_settings.EMAIL_HOST_USER, subscriber.email, msg
                    )
        except Exception as e:
            return str(e)
        task.deadline_notified = True
        task.save()


@shared_task
def send_task_status_update_notification(
    email_list, task_title: str, old_status: str, new_status: str
):
    try:
        with smtplib.SMTP(lazy_settings.EMAIL_HOST, lazy_settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(
                lazy_settings.EMAIL_HOST_USER, lazy_settings.EMAIL_HOST_PASSWORD
            )
            msg = f'You are notified that the status of task "{task_title}" has been changed from "{old_status}" to "{new_status}".'
            for to_email in email_list:
                server.sendmail(lazy_settings.EMAIL_HOST_USER, to_email, msg)
        return 'Email sent successfully!'
    except Exception as e:
        return str(e)


@shared_task
def send_join_to_project_notification(to_email, project_title: str):
    try:
        with smtplib.SMTP(lazy_settings.EMAIL_HOST, lazy_settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(
                lazy_settings.EMAIL_HOST_USER, lazy_settings.EMAIL_HOST_PASSWORD
            )
            msg = f'We would like to inform you that you have been added to Project "{project_title}".'
            server.sendmail(lazy_settings.EMAIL_HOST_USER, to_email, msg)
        return 'Email sent successfully!'
    except Exception as e:
        return str(e)


@shared_task
def send_subscription_on_task_notification(to_email, task_title: str):
    try:
        with smtplib.SMTP(lazy_settings.EMAIL_HOST, lazy_settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(
                lazy_settings.EMAIL_HOST_USER, lazy_settings.EMAIL_HOST_PASSWORD
            )
            msg = f'We would like to inform you that you have subscribed to Task "{task_title}".'
            server.sendmail(lazy_settings.EMAIL_HOST_USER, to_email, msg)
        return 'Email sent successfully!'
    except Exception as e:
        return str(e)
