from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
from config import get_settings, logger
import smtplib

settings = get_settings()

def send(subject:str, recipient: str, template_name:str, context: dict):
    try:
        message = MIMEMultipart('alternative')
        message['From'] = settings.smtp_email_from
        message['To'] = ', '.join(recipient) if type(recipient) == list else recipient
        message['Subject'] = subject

        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template(template_name)
        html_content = template.render(context)

        html_part = MIMEText(html_content, 'html')
        message.attach(html_part)

        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            
            if isinstance(recipient, list):
                server.sendmail(message['From'], recipient, message.as_string())
            else:
                server.sendmail(message['From'], message['To'], message.as_string())
    
    except Exception as e:
        logger.error(str(e))
