from datetime import datetime, timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from app.model.user import Token, UserDocument
from app.schemas import user as user_schema
from app.utils import ACCESS_TOKEN_EXPIRE_MINUTES, TokenManager
from app.conf import smtp


router = APIRouter(prefix="/user")
authrouter = APIRouter(prefix="/auth")


@router.post(
        "",
        tags=["User"],
        status_code=status.HTTP_201_CREATED,
        summary="Create a user"
)
async def create_user(user: user_schema.UserCreate) -> Dict[str, Any]:
    """
    Create a new user or log in an existing user.

    This endpoint handles both user creation and user login.
    If the username already exists, it will verify the password
                                         and log the user in.
    If the username does not exist, it will create a new user
                                 with the provided credentials.

    Args:
        user (UserCreate): UserCreate schema containing username and password.

    Raises:
        HTTPException: If the username already exists but
                                        the password is incorrect.
        HTTPException: If there is any error during
                                        the user creation or login process.

    Returns:
        dict: A dictionary containing a success message.
    """

    if user.username in await UserDocument.find().to_list():
        # Handle login
        user_in_db = UserDocument[user.username]
        if not TokenManager.verify_password(
                user.password,
                user_in_db.hashed_password
                ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )
    else:
        # Handle user creation
        user_name = user.username
        hashed_password = TokenManager.get_password_hash(user.password)
        # redis_client = smtp.RedisClient()
        # redis_client.set_with_ttl('otp', _otp, 10)
        _user = UserDocument(
            username=user_name,
            password=hashed_password,
            hashed_password=hashed_password,
            email=user.email,
            role="Admin",
            mfa=user.is_mfa,
            is_enabled=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        await _user.insert()
    return {
        "msg": "User created in successfully",
    }


@router.get(
        "",
        tags=["User"],
        summary="Read Users")
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(25, ge=1),
) -> Dict[str, Any]:
    """
    Get a list of users with pagination.

    Args:
        skip (int): The number of records to skip.
        limit (int): The number of records to return.

    Returns:
        Dict[str, Any]: A dictionary containing a list of users.
    """
    users_in_db = await UserDocument.find().skip(skip).limit(limit).to_list()
    all_data_count = await UserDocument.count()

    return {
        "users": [
            {
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "is_enabled": user.is_enabled,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
            }
            for user in users_in_db
        ],
        "total": all_data_count,
        "skip": skip,
        "limit": limit,
    }


@router.patch(
        "/{username}",
        tags=["User"],
        summary="Update User")
async def update_user(
    username: str,
    user_update: user_schema.UpdateUser,
) -> Dict[str, Any]:
    """
    Update a user's information.

    Args:
        username (str): The username of the user to update.
        user_update (UpdateUser): The user information to update.

    Raises:
        HTTPException: If the user is not found in the database.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(UserDocument.username == username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user_in_db, key, value)
    user_in_db.updated_at = datetime.utcnow()
    await user_in_db.save()

    return {"msg": "User updated successfully"}


@router.get(
        "/{username}",
        tags=["User"],
        summary="Get User Details"
    )
async def get_user_details(
    username: str,
) -> Dict[str, Any]:
    """
    Get the details of a specific user by username.

    Args:
        username (str): The username of the user to retrieve.

    Raises:
        HTTPException: If the user is not found in the database.

    Returns:
        Dict[str, Any]: A dictionary containing user details.
    """
    user_in_db = await UserDocument.find_one(UserDocument.username == username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return {
        "username": user_in_db.username,
        "email": user_in_db.email,
        "role": user_in_db.role,
        "is_enabled": user_in_db.is_enabled,
        "created_at": user_in_db.created_at,
        "updated_at": user_in_db.updated_at,
    }


@router.post(
        "/token_verify",
        tags=["User"],
        summary="Verify Token"
    )
async def verify_token(
    request: Request,
    token_data: user_schema.TokenData = Depends(
        TokenManager.decode_access_token),
) -> Dict[str, Any]:
    """
    Verify the provided token and update user verification status.

    This endpoint verifies the provided JWT token and updates the user's
    verification status in the database.

    Args:
        token_data (TokenData, optional):
            TokenData schema containing the username from the token.
            Defaults to Depends(TokenManager.decode_access_token).

    Raises:
        HTTPException: If the user is not found in the database.
        HTTPException: If there is any error during the verification process.

    Returns:
        dict: A dictionary containing a success message.
    """

    print(request.user.display_name)
    # Find the user in the database using the username from the token
    user_in_db = await UserDocument.find_one(
        UserDocument.username == token_data.username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update the is_verify field to True
    user_in_db.is_verify = True
    user_in_db.updated_at = datetime.utcnow()  # Update the updated_at field
    await user_in_db.save()

    return {"msg": "Token is valid and user verification updated"}


@router.patch(
        "",
        tags=["User"],
        summary="Change Password for User"
    )
async def change_password(
    change_password: user_schema.ChangePassword,
    token_data: user_schema.TokenData = Depends(
        TokenManager.decode_access_token),
) -> Dict[str, Any]:
    """
    Change the password for an authenticated user.

    This endpoint allows an authenticated user to change their password
    by providing the old password and the new password.

    Args:
        change_password (ChangePassword):
            ChangePassword schema containing the old and new passwords.
        token_data (TokenData, optional):
            TokenData schema containing the username from the token.
            Defaults to Depends(TokenManager.decode_access_token).

    Raises:
        HTTPException: If the user is not found in the database.
        HTTPException: If the old password is incorrect.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(
        UserDocument.username == token_data.username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not TokenManager.verify_password(
        change_password.old_password, user_in_db.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password",
        )

    if change_password.new_password != change_password.verify_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and verify new password do not match",
        )

    new_hashed_password = TokenManager.get_password_hash(
        change_password.new_password
    )
    user_in_db.hashed_password = new_hashed_password
    user_in_db.password = new_hashed_password
    user_in_db.updated_at = datetime.utcnow()
    await user_in_db.save()

    return {"msg": "Password changed successfully"}


@router.delete(
        "/{username}",
        tags=["User"],
        summary="Delete User"
        )
async def delete_user(
    username: str,
    token_data: user_schema.TokenData = Depends(
        TokenManager.decode_access_token),
) -> Dict[str, Any]:
    """
    Delete a user by username.

    This endpoint allows an authenticated user (or an admin) to delete a user
    by providing the username.

    Args:
        username (str): The username of the user to delete.
        token_data (TokenData, optional): TokenData schema containing the
                                        username from the token. Defaults to
                                        Depends(TokenManager.decode_access_token).

    Raises:
        HTTPException: If the user is not found in the database.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(UserDocument.username == username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await user_in_db.delete()

    return {"msg": "User deleted successfully"}


@router.post(
        "/mfa",
        tags=["MFA"],
        summary="MFA Service"
    )
async def mfa_enabled(
    request: Request,
    mfa_data: user_schema.MFAUpdate
) -> Dict[str, Any]:
    """
    Enable or Disable MFA for a user.

    Args:
        mfa_data (MFAUpdate): Schema containing the username and MFA status.

    Raises:
        HTTPException: If the user is not found in the database.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(
        UserDocument.username == mfa_data.username)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_in_db.is_mfa = mfa_data.is_mfa
    user_in_db.updated_at = datetime.utcnow()
    await user_in_db.save()

    status_msg = "enabled" if mfa_data.is_mfa else "disabled"
    return {"msg": f"MFA {status_msg} successfully"}


@authrouter.post(
        "",
        tags=["Auth"],
        summary="Login to a User"
    )
async def login_user(
    request: Request,
    user: user_schema.UserLogin
) -> Dict[str, Any]:
    """
    Login an existing user and return an access token.

    This endpoint verifies the user's credentials and generates a
                    JWT access token if the credentials are correct.

    Args:
        user (UserLogin): UserLogin schema containing username and password.

    Raises:
        HTTPException: If the username is not found or
                                    the password is incorrect.
        HTTPException: If there is any error during the login process.

    Returns:
        dict: A dictionary containing a success message,
                                access token, and token type.
    """
    user_in_db = await UserDocument.find_one(
            UserDocument.username == user.username)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username  or password",
        )

    if not TokenManager.verify_password(
            user.password,
            user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if user_in_db.is_mfa:
        if not user_in_db.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=("Activate MFA for enhanced security features, "
                        "If mfa is Enabled then Please update your email "
                        "in user settings for OTP verification."),
            )

        otp = smtp.generate_otp()
        host = request.client.host
        key = f'user-otp-{user.username}-{host}'
        value = otp
        _redis = smtp.RedisClient()
        _redis.set_with_ttl(key, value, 120)
        # user_in_db.otp = otp
        # await user_in_db.save()

        email_body = f"Your OTP code is {otp}"
        await smtp.send_otp(
            email_to=user_in_db.email,
            subject="Your OTP Code",
            body=email_body
        )
        return {
            "msg": "OTP sent to your email and otp is expired in 2 minites",
        }

    # Generate and return access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = TokenManager.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    host = request.client.host
    key = f'user-token-{user.username}-{host}'
    value = access_token
    _redis = smtp.RedisClient()
    _redis.set_with_ttl(key, value, 1800)
    await Token(
        username=user.username,
        token=access_token,
        active=False,
        created_at=datetime.utcnow(),
    ).insert()

    return {
        "msg": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
    }


@authrouter.post(
        "/verifyotp",
        tags=["Auth"],
        summary="Verify OTP")
async def verify_otp(
    request: Request,
    user: user_schema.Verifyotp
) -> Dict[str, Any]:
    """
    Verify the OTP provided by the user.

    Args:
        username (str): The username of the user to verify the OTP for.
        otp (str): The OTP code provided by the user.

    Raises:
        HTTPException: If the user is not found in the database.
        HTTPException: If the OTP is incorrect or expired.

    Returns:
        Dict[str, Any]: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(
        UserDocument.username == user.username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    host = request.client.host
    key = f'user-otp-{user.username}-{host}'
    _redis = smtp.RedisClient()
    _otp = _redis.get_key(key)
    if not _otp:
        return dict(desc='OTP is Expired please reagain login')
    _otp = _otp.decode()
    if _otp != user.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    # Clear OTP after successful verification
    user_in_db.otp = None
    user_in_db.updated_at = datetime.utcnow()
    await user_in_db.save()

    # Generate and return access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = TokenManager.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    host = request.client.host
    key = f'user-token-{user.username}-{host}'
    value = access_token
    _redis = smtp.RedisClient()
    _redis.set_with_ttl(key, value, 1800)
    await Token(
        username=user.username,
        token=access_token,
        active=False,
        created_at=datetime.utcnow(),
    ).insert()

    return {
        "msg": "OTP verified and Login successfully",
        "access_token": access_token,
        "token_type": "bearer",
    }


@authrouter.delete(
        "",
        tags=["Auth"],
        summary="Logout User"
    )
async def logout_user(
    request: Request,
    token_data: user_schema.TokenData = Depends(
        TokenManager.decode_access_token),
) -> Dict[str, Any]:
    """
    Logout the user by marking them as deleted and deactivating their token.

    This endpoint logs out the user by setting the is_delete flag to True
    and updating the token status in the database.

    Args:
        token_data (TokenData, optional):
            TokenData schema containing the username from the token.
            Defaults to Depends(TokenManager.decode_access_token).

    Raises:
        HTTPException: If the user is not found in the database.
        HTTPException: If there is any error during the logout process.

    Returns:
        dict: A dictionary containing a success message.
    """
    user_in_db = await UserDocument.find_one(
        UserDocument.username == token_data.username)

    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user_in_db.is_delete = True
    user_in_db.updated_at = datetime.utcnow()
    try:
        await user_in_db.save()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging out user: {e}",
        )
    # await user_in_db.save()
    try:
        # trunk-ignore(bandit/B106)
        await Token(
            username=request.user.display_name, # noqa
            token="",
            active=False,
            created_at=datetime.utcnow(),
        ).insert()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deactivating token: {e}",
        )
    return {"msg": "User logged out successfully"}
