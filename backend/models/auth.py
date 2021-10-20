from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class User(Model):
    id = fields.IntField(pk=True, index=True)
    email = fields.CharField(max_length=100, null=False, unique=True)
    name = fields.CharField(max_length=100, null=False, unique=True)
    password = fields.CharField(max_length=128, null=False)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    @classmethod
    def get_hashed_password(cls, password):
        return pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)


user_pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
userRegister_pydantic = pydantic_model_creator(User, name="UserRegister", include=("email", "name", "password"))
userLogin_pydantic = pydantic_model_creator(User, name="UserLogin", include=("email", "password"))
userResetPassword_pydantic = pydantic_model_creator(User, name="UserResetPassword", include=("email", ))


class ResetPasswordReq(BaseModel):
    uidb64: str
    token: str
    password: str