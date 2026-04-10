
from pydantic import BaseModel


class PasswordCheckRequest(BaseModel):
    password: str
