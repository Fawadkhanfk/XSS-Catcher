from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, BaseSettings, EmailStr, HttpUrl


class Settings(BaseSettings):
    authjwt_secret_key: str


@AuthJWT.load_config
def get_config():
    return Settings()


class User(BaseModel):
    id: int
    username: str
    password_hash: str
    first_login: bool
    is_admin: bool

    class Config:
        orm_mode = True


class Client(BaseModel):
    id: int
    uid: str
    name: str
    description: str
    mail_to: EmailStr
    webhook_url: HttpUrl

    class Config:
        orm_mode = True
