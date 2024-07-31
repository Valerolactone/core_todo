import logging
import smtplib
from datetime import datetime, timedelta
from itertools import zip_longest

from api.models import Task, TaskNotification, TaskSubscriber
from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)


def send_notification(recipient: str, subject: str, body: str):
    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg = f'Subject: {subject}\n\n{body}'
            server.sendmail(settings.EMAIL_HOST_USER, recipient, msg)
            logger.info(f'Email sent to {recipient} with subject: "{subject}"')
    except smtplib.SMTPConnectError:
        logger.error(
            f'Error sending email to {recipient}: Failed to connect to SMTP server.'
        )
    except smtplib.SMTPAuthenticationError:
        logger.error(
            f'Error sending email to {recipient}: Invalid credentials for SMTP server.'
        )
    except smtplib.SMTPServerDisconnected:
        logger.error(
            f'Error sending email to {recipient}: SMTP server was disconnected.'
        )
    except smtplib.SMTPException as e:
        logger.error(f'SMTP error sending email to {recipient}: {str(e)}')
    except TypeError as e:
        logger.error(f'Type error sending email to {recipient}: {str(e)}')
    except Exception as e:
        logger.error(f'Error sending email to {recipient}: {str(e)}')


def send_notification_to_all_subscribers(
    recipients_dict: dict, subject: str, body: str, task_id: int, notification_type: str
):
    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            msg = f'Subject: {subject}\n\n{body}'
            for recipient in recipients_dict:
                if not TaskNotification.objects.filter(
                    task=task_id,
                    notified_user_id=recipient.key(),
                    notification_type=notification_type,
                ).exist():
                    server.sendmail(settings.EMAIL_HOST_USER, recipient.value(), msg)
                    TaskNotification.objects.create(
                        task=task_id,
                        notified_user_id=recipient.key(),
                        notification_type=notification_type,
                    )
                logger.info(
                    f'Email sent to {recipient.value()} with subject: "{subject}"'
                )
    except smtplib.SMTPConnectError:
        logger.error(
            f'Error sending email to {recipient}: Failed to connect to SMTP server.'
        )
    except smtplib.SMTPAuthenticationError:
        logger.error(
            f'Error sending email to {recipient}: Invalid credentials for SMTP server.'
        )
    except smtplib.SMTPServerDisconnected:
        logger.error(
            f'Error sending email to {recipient}: SMTP server was disconnected.'
        )
    except smtplib.SMTPException as e:
        logger.error(f'SMTP error sending email to {recipient}: {str(e)}')
    except TypeError as e:
        logger.error(f'Type error sending email to {recipient}: {str(e)}')
    except Exception as e:
        logger.error(f'Error sending email to {recipient}: {str(e)}')


@shared_task
def send_task_deadline_notification():
    now = datetime.utcnow()
    one_hour_from_now = now + timedelta(hours=1)
    tasks_due_soon = Task.objects.filter(due_date__lte=one_hour_from_now)
    for task in tasks_due_soon:
        subject = "Task Deadline Notification"
        body = f"There's an hour left until the deadline for task {task.title}."
        # TODO: получить потом имейлы и переписать логику с zip_longest
        subscribers = TaskSubscriber.objects.filter(task=task).values_list(
            'subscriber_id', flat=True
        )
        emails = [settings.TEST_EMAIL_FOR_CELERY, settings.TEST_EMAIL_FOR_CELERY_1]
        recipients_dict = dict(
            zip_longest(subscribers, emails, fillvalue=settings.TEST_EMAIL_FOR_CELERY)
        )
        send_notification_to_all_subscribers(
            recipients_dict, subject, body, task.task_pk, 'deadline'
        )


@shared_task
def send_task_status_update_notification(
    task_title: str, old_status: str, new_status: str
):
    subject = "Task Status Update Notification"
    body = f'You are notified that the status of task "{task_title}" has been changed from "{old_status}" to "{new_status}".'
    task = Task.objects.get(title=task_title)
    # TODO: получить потом имейлы и переписать логику с zip_longest
    subscribers = TaskSubscriber.objects.filter(task=task).values_list(
        'subscriber_id', flat=True
    )
    emails = [settings.TEST_EMAIL_FOR_CELERY, settings.TEST_EMAIL_FOR_CELERY_1]
    recipients_dict = dict(
        zip_longest(subscribers, emails, fillvalue=settings.TEST_EMAIL_FOR_CELERY)
    )
    send_notification_to_all_subscribers(
        recipients_dict, subject, body, task.task_pk, 'update status'
    )


@shared_task
def send_join_to_project_notification(recipient_email: str, project_title: str):
    subject = 'You have been added to a project'
    body = f'We would like to inform you that you have been added to Project "{project_title}".'
    send_notification(recipient_email, subject, body)


@shared_task
def send_subscription_on_task_notification(recipient_email: str, task_title: str):
    subject = 'Subscription to task notification'
    body = (
        f'We would like to inform you that you have subscribed to Task "{task_title}".'
    )
    send_notification(recipient_email, subject, body)
