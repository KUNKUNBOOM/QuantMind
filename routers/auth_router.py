import string
from aiosmtplib import SMTPResponseException
from fastapi import APIRouter, Query, Depends, HTTPException
from pydantic import EmailStr
from typing import Annotated
from core.auth import AuthHandler
from dependencies import get_mail, get_session
from schemas.user import RegisterIn, LoginIn, LoginOut, ChangePasswordIn
from fastapi_mail import FastMail, MessageSchema, MessageType
from models import AsyncSession
import random
from repository.user_repo import EmailCodeRePository, UserRepository
from schemas import ResponseOut

auth_handler = AuthHandler()
router = APIRouter(prefix="/auth", tags=["user"])


@router.get("/code", response_model=ResponseOut)
async def get_email_code(
        email: Annotated[EmailStr, Query(...)],
        mail: FastMail = Depends(get_mail),
        session: AsyncSession = Depends(get_session),
):
    source = string.digits * 4
    code = "".join(random.sample(source, 4))
    message = MessageSchema(
        subject="注册验证码",
        recipients=[email],
        body=f"您的验证码为{code}，五分钟内有效！",
        subtype=MessageType.plain
    )
    try:
        await mail.send_message(message)
    except SMTPResponseException as e:
        if not (e.code == -1 and b"\\x00\\x00\\x00" in str(e).encode()):
            raise HTTPException(500, detail="邮件发送失败")
    email_code_repo = EmailCodeRePository(session=session)
    await email_code_repo.create(str(email), code)
    return ResponseOut()


@router.post("/register", response_model=ResponseOut)
async def register(data: RegisterIn, session: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session=session)
    if await user_repo.email_is_exist(email=str(data.email)):
        raise HTTPException(400, detail="邮箱已经存在")
    email_code_repo = EmailCodeRePository(session=session)
    if not await email_code_repo.check_email_code(email=str(data.email), code=str(data.code)):
        raise HTTPException(400, detail="邮箱或者验证码错误")
    try:
        await user_repo.create(data)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    return ResponseOut()


@router.post("/login", response_model=LoginOut)
async def login(data: LoginIn, session: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_email(str(data.email))
    if not user:
        raise HTTPException(400, detail="该用户不存在")
    if not user.check_password(str(data.password)):
        raise HTTPException(400, detail="邮箱或者密码错误！")
    tokens = auth_handler.encode_login_token(user.id)
    return {"user": user, "token": tokens['access_token']}


@router.post("/change-password", response_model=ResponseOut)
async def change_password(
        data: ChangePasswordIn,
        user_id: int = Depends(auth_handler.auth_access_dependency),
        session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(400, detail="用户不存在")
    if not user.check_password(str(data.old_password)):
        raise HTTPException(400, detail="原密码错误")
    await user_repo.change_password(user_id, str(data.new_password))
    return ResponseOut()
