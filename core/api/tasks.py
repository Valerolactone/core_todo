import os
import smtplib
from email.mime.text import MIMEText

from celery import shared_task

'''@shared_task
def send_task_status_update_notification(email, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return str(e)'''
