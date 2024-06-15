from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    phone_number: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    role: Union[str, None] = None


class UserRead(BaseModel):
    username: str
    phone_number: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    role: str


class UserUpdate(BaseModel):
    username: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    phone_number: Union[str, None] = None


class UserCreate(BaseModel):
    username: str
    password: str
    phone_number: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None


class ResetPasswordData(BaseModel):
    username: str
    phone_number: str


class NewPasswordData(BaseModel):
    username: str
    phone_number: str
    reset_password_code: str
    new_password: str
