import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from datetime import datetime
from enum import Enum
import settings
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

# 安装依赖：pip install pyjwt==2.10.1
from threading import Lock


class SingletonMeta(type):
    """
    线程安全的单例模式元类
    """
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            return cls._instances[cls]


class TokenTypeEnum(Enum):
    ACCESS_TOKEN = 1
    REFRESH_TOKEN = 2


class AuthHandler(metaclass=SingletonMeta):
    security = HTTPBearer()
    # 请求头格式：Authorization: Bearer {token}

    secret = settings.JWT_SECRET_KEY

    def _encode_token(self, user_id: int, type: TokenTypeEnum):
        payload = dict(
            iss=str(user_id),
            sub=str(type.value)
        )
        to_encode = payload.copy()
        # 改用utcnow，避免时区问题
        if type == TokenTypeEnum.ACCESS_TOKEN:
            exp = datetime.utcnow() + settings.JWT_ACCESS_TOKEN_EXPIRES
        else:
            exp = datetime.utcnow() + settings.JWT_REFRESH_TOKEN_EXPIRES
        to_encode.update({"exp": int(exp.timestamp())})

        # 🔥 核心修改：显式转换为字符串 str()，100%保证是str类型
        return str(jwt.encode(to_encode, self.secret, algorithm='HS256'))

    def encode_login_token(self, user_id: int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        refresh_token = self._encode_token(user_id, TokenTypeEnum.REFRESH_TOKEN)
        # 因为上面已经转str，这里直接赋值即可，无需多余f-string
        login_token = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        return login_token

    def encode_update_token(self, user_id: int):
        access_token = self._encode_token(user_id, TokenTypeEnum.ACCESS_TOKEN)
        update_token = {
            "access_token": access_token
        }
        return update_token

    def decode_access_token(self, token: str):
        """解析并验证 Access Token，失败返回403"""
        try:


            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if str(payload['sub']) != str(TokenTypeEnum.ACCESS_TOKEN.value):
                raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Token类型错误!')
            return int(payload['iss'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token已过期')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail='Access Token不可用')

    def decode_refresh_token(self, token: str):
        """解析并验证 Refresh Token，失败返回401"""
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if str(payload['sub']) != str(TokenTypeEnum.REFRESH_TOKEN.value):
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Token类型错误!')
            return int(payload['iss'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token已过期')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail='Refresh Token不可用')

    def auth_access_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """FastAPI 依赖项：验证 Access Token"""
        return self.decode_access_token(auth.credentials)

    def auth_refresh_dependency(self, auth: HTTPAuthorizationCredentials = Security(security)):
        """FastAPI 依赖项：验证 Refresh Token"""
        return self.decode_refresh_token(auth.credentials)