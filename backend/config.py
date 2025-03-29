from pydantic import BaseModel
from fastapi_mail import ConnectionConfig

class EmailSettings(BaseModel):
    MAIL_USERNAME: str = "your-email@gmail.com"
    MAIL_PASSWORD: str = "your-email-password"
    MAIL_FROM: str = "your-email@gmail.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

email_config = EmailSettings()

conf = ConnectionConfig(
    MAIL_USERNAME=email_config.MAIL_USERNAME,
    MAIL_PASSWORD=email_config.MAIL_PASSWORD,
    MAIL_FROM=email_config.MAIL_FROM,
    MAIL_PORT=email_config.MAIL_PORT,
    MAIL_SERVER=email_config.MAIL_SERVER,
    MAIL_TLS=email_config.MAIL_TLS,
    MAIL_SSL=email_config.MAIL_SSL
)
