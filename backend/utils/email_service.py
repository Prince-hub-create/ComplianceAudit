from fastapi_mail import FastMail, MessageSchema
from config import conf

async def send_email(subject: str, recipients: list, body: str):
    """Send email notifications"""
    message = MessageSchema(
        subject=subject,
        recipients=recipients,  # List of recipient emails
        body=body,
        subtype="html",
    )
    mail = FastMail(conf)
    await mail.send_message(message)
