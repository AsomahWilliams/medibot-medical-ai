from pydantic import BaseModel, EmailStr, Field

class SignupSchema(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)

class LoginSchema(BaseModel):
    email: EmailStr
    password: str