from http.client import HTTPException
import random
import smtplib
import redis
from typing import List
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.model.user import EmailConfigDocument
from fastapi import status
from datetime import datetime, timedelta
import time


class EmailError(Exception):
    """Custom exception for email errors"""
    pass


async def send_email_async(subject: str, email_to: List[str], body: dict):
    try:
        email_config = await EmailConfigDocument.find_one({})
        if not email_config:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email configuration not found",
            )

        sender_email = email_config.sender_email
        receiver_email = email_to

        message = MIMEMultipart()
        message["From"] = email_config.sender_name
        message["To"] = ", ".join(email_to)
        message["Subject"] = subject

        _body = f"""\n Hi {body.get("email") }\n\n Thanks for registering as
                {body.get("project_name")}!\n\n please find your verification
                URL here {body.get("url")}"""
        message.attach(MIMEText(_body, "plain"))
        try:
            with smtplib.SMTP(email_config.smtp_server) as server:
                if email_config.use_tls:
                    server.starttls()
                if email_config.smtp_username and email_config.smtp_password:
                    server.login(
                        email_config.smtp_username, email_config.smtp_password)
                text = message.as_string()
                server.sendmail(sender_email, receiver_email, text)
        except smtplib.SMTPAuthenticationError:
            raise EmailError("SMTP authentication error. "
                             "Please check your username and password.")
        except smtplib.SMTPConnectError:
            raise EmailError("Failed to connect to the SMTP server. "
                             "Please check the server address and port.")
        except smtplib.SMTPRecipientsRefused:
            raise EmailError("All recipients were refused. "
                             "Please check the recipient email addresses.")
        except smtplib.SMTPSenderRefused:
            raise EmailError("The sender address was refused. "
                             "Please check the sender email address.")
        except smtplib.SMTPDataError:
            raise EmailError("The SMTP server refused to accept the message")
        except smtplib.SMTPException as e:
            raise EmailError(f'An SMTP error occurred: {e}')
        except Exception as e:
            raise EmailError(f'An unexpected error occurred: {e}')

    except EmailError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Failed to send email: {e}'
        )
    except HTTPException as e:
        # Re-raise the HTTPException if it's from the email configuration block
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An unexpected error occurred: {e}'
        )


async def send_otp(email_to, subject, body):
    email_config = await EmailConfigDocument.find_one({})
    if not email_config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email configuration not found",
        )

    message = MIMEMultipart()
    sender_email = email_config.sender_email
    message["From"] = email_config.sender_name
    message["To"] = email_to
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to SMTP server
        with smtplib.SMTP(email_config.smtp_server) as server:
            text = message.as_string()
            server.sendmail(sender_email, email_to, text)
            print('Email sent successfully')
    except Exception as e:
        raise EmailError(f'An unexpected error occurred: {e}')
    finally:
        try:
            server.quit()
        except Exception as e:
            print(f'Error while closing the SMTP server connection: {e}')


def generate_otp():
    # Generate a random number with the specified length
    # trunk-ignore(bandit/B311)
    _random_range = random.randint(111, 999999)
    _final_number = str(_random_range)
    return _final_number


class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        print(f"Connected to Redis server at {host}:{port}")

    def __del__(self):
        print("Closing Redis connection")
        del self.client

    def set_with_ttl(self, key, value, ttl):
        self.client.setex(key, ttl, value)
        print(f"Set key '{key}' with value '{value}' and TTL of {ttl} seconds")

    def get_key(self, key):
        value = self.client.get(key)
        return value


def send_otp_with_countdown():
    expiry_time = datetime.now() + timedelta(minutes=1)
    while True:
        remaining_time = expiry_time - datetime.now()
        if remaining_time.total_seconds() <= 0:
            print("OTP has expired.")
            break

        # Format the remaining time as minutes and seconds
        minutes, seconds = divmod(remaining_time.total_seconds(), 60)
        countdown = f"{int(minutes):02d}:{int(seconds):02d} remaining"

        print(f"\rTime left for OTP expiry: {countdown}", end="")
        time.sleep(1)
