from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from app.model.user import EmailConfigDocument
from app.schemas import user
from typing import List
import asyncio

router = APIRouter(prefix="/smtp")


@router.post(
    "",
    tags=["SMTP"],
    status_code=status.HTTP_201_CREATED,
    summary="Configure SMTP Settings",
)
async def configure_smtp(config: user.EmailConfig) -> Dict[str, Any]:
    """
    Configure the SMTP settings for sending emails.

    Args:
        config (EmailConfig): Schema containing the SMTP configuration.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    email_config = EmailConfigDocument(
        smtp_server=config.smtp_server,
        smtp_port=config.smtp_port,
        sender_email=config.sender_email,
        sender_name=config.sender_name,
        smtp_username=config.smtp_username,
        smtp_password=config.smtp_password,
        use_tls=config.use_tls,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    await email_config.save()
    return {"msg": "SMTP configuration saved successfully"}


@router.patch(
    "",
    tags=["SMTP"],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Update Email Configuration",
)
async def update_email_config(config: user.UpdateEmailConfig) -> Dict[str, Any]:
    """
    Update the email configuration.

    Args:
        config (UpdateEmailConfig): Schema containing the
                    updated email configuration.

    Raises:
        HTTPException: If no email configuration is found.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    email_config = await EmailConfigDocument.find_one({})
    if not email_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found",
        )

    if config.smtp_server:
        email_config.smtp_server = config.smtp_server
    if config.smtp_port:
        email_config.smtp_port = config.smtp_port
    if config.sender_email:
        email_config.sender_email = config.sender_email
    if config.sender_name:
        email_config.sender_name = config.sender_name
    if config.smtp_username:
        email_config.smtp_username = config.smtp_username
    if config.smtp_password:
        email_config.smtp_password = config.smtp_password
    if config.use_tls is not None:
        email_config.use_tls = config.use_tls

    email_config.updated_at = datetime.utcnow()
    await email_config.save()
    return {"msg": "Email configuration updated successfully"}


@router.delete(
    "",
    tags=["SMTP"],
    status_code=status.HTTP_201_CREATED,
    summary="Delete Email Configuration",
)
async def delete_email_config() -> Dict[str, Any]:
    """
    Delete the email configuration.

    Raises:
        HTTPException: If no email configuration is found.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    email_config = await EmailConfigDocument.find_one({})
    if not email_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found",
        )

    await email_config.delete()
    return {"msg": "Email configuration deleted successfully"}


@router.get("", tags=["SMTP"], summary="Get SMTP Information")
async def get_smtp_info() -> Dict[str, Any]:
    """
    Get the current SMTP configuration.

    Raises:
        HTTPException: If no email configuration is found.

    Returns:
        Dict[str, Any]: A dictionary containing the SMTP configuration.
    """
    email_config = await EmailConfigDocument.find_one({})
    if not email_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email configuration not found",
        )

    return {
        "smtp_server": email_config.smtp_server,
        "smtp_port": email_config.smtp_port,
        "sender_email": email_config.sender_email,
        "sender_name": email_config.sender_name,
        "smtp_username": email_config.smtp_username,
        "use_tls": email_config.use_tls,
        "created_at": email_config.created_at,
        "updated_at": email_config.updated_at,
    }


