from pydantic import BaseModel


class ResponseOut(BaseModel):
    code: int = 0
    msg: str = "ok"
