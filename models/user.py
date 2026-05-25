# models/user.py
import datetime

from . import Base
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped,mapped_column,relationship
from typing import List
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


class User(Base):
    __tablename__ = "user"
    id:Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email:Mapped[str] = mapped_column(String(100), unique=True,index=True)
    username:Mapped[str] = mapped_column(String(100))
    _password:Mapped[str] = mapped_column(String(200))

    def __init__(self,*args,**kwargs):
        password=kwargs.pop("password")  # 从参数中取出password
        super().__init__(*args,**kwargs)
        if password:
            # 错误：self.set_password(password) 
            # 正确：触发password的setter方法
            self.password = password  

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self,raw_password):
        self._password=password_hash.hash(raw_password)

    def check_password(self,raw_password):
        return password_hash.verify(raw_password,self._password)

class EmailCode(Base):
    __tablename__ = "email_code"
    id:Mapped[int] = mapped_column(Integer, primary_key=True,autoincrement=True)
    email:Mapped[str] = mapped_column(String(100))
    code:Mapped[str] = mapped_column(String(100))
    created_time:Mapped[datetime] = mapped_column(DateTime,default=datetime.datetime.now)