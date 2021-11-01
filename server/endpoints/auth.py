import pydantic
from fastapi import APIRouter, Response
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from models import User

router = APIRouter()


@router.exception_handler(AuthJWTException)
def authjwt_exception_handler(exception: AuthJWTException):
    return {"status_code": exception.status_code, "content": {"detail": exception.message}}


class LoginRequest(pydantic.BaseModel):
    username: str
    password: str


@router.post("/login")
def login(user: LoginRequest, authorize: AuthJWT, response: Response):
    if authorize.get_jwt_subject():
        response.status_code = 400
        return {"message": "Already logged in"}

    user = User.query()

    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    # subject identifier for who this token is for example id or username from database
    access_token = Authorize.create_access_token(subject=user.username)
    return {"access_token": access_token}
