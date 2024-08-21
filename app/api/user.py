from fastapi import APIRouter, HTTPException, Depends
from schemas import user as SchemasUser
from db.model import user as UserModel
from sqlalchemy.orm import Session
from db.sesssion import SessionLocal, engine
from . import crud
from fastapi.security import OAuth2PasswordBearer
from app.core.security import hash_password, hash_verify
from typing import List
from app.core.jwt_config import create_access_token, decode_token, get_current_user1
import jwt
from jwt import PyJWTError
from typing import Optional
from typing import Annotated
from app.api.crud import get_user_by_user_name
from fastapi import Security, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from sqlalchemy.orm import Session
from schemas.user import TokenData
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="user/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)
UserModel.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception
    user = get_user_by_user_name(db, user_name=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(
    current_user: Annotated[
        SchemasUser.UserCreate, Security(get_current_user, scopes=["me"])
    ],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.get("/{user_id}", response_model=SchemasUser.User)
def read_user(
    id_user: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    db_user = crud.get_user(db=db, user_id=id_user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return db_user


@router.get("/", response_model=List[SchemasUser.User])
def read_users(
    skip: int = 0,
    limit: int = 100,
    order_by: str = "id",
    order_direction: str = "desc",
    db: Session = Depends(get_db),
):
    users = crud.get_users(
        db=db,
        skip=skip,
        limit=limit,
        order_by=order_by,
        order_direction=order_direction,
    )
    return users


@router.post("/create", response_model=SchemasUser.User)
def create_user(user: SchemasUser.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@router.delete("/delete/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is not None:
        crud.delete_user_by_id(db=db, user_id=user_id)
        raise HTTPException(status_code=200, detail="user deleted")
    else:
        raise HTTPException(status_code=404, detail="user not found")


@router.put("/update/{user_id}", response_model=SchemasUser.User)
def updata_user(
    user_id: int,
    user_update: SchemasUser.UserUpdate,
    current_user: str = Depends(get_current_user1),
    db: Session = Depends(get_db),
):

    db_user = crud.get_user(db=db, user_id=user_id)
    if db_user is not None:
        if current_user["sub"] != db_user.user_name:
            raise HTTPException(
                status_code=403, detail="Not authorized to update this user"
            )
        crud.update_user(db=db, user_id=user_id, user_update=user_update)
        raise HTTPException(status_code=200, detail="user changed")
    else:
        raise HTTPException(status_code=404, detail="user not found")


# @router.post("/token1", response_model=SchemasUser.Token)
# def aithentication(user: SchemasUser.UserLogin, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_user_name(db=db, user_name=user.user_name)
#     if db_user is None:
#         raise HTTPException(status_code=401, detail="user not found")

#     if hash_verify(hashe_pass=db_user.password, password=user.password):
#         access_token = create_access_token(data={"subname": user.user_name})
#         return {"access_token": access_token, "token_type": "bearer"}
#     raise HTTPException(status_code=401, detail="Incorrect username or password")


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={"sub": user.user_name, "scopes": form_data.scopes},
    )
    return SchemasUser.Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=SchemasUser.User)
async def read_users_me(
    current_user: Annotated[SchemasUser.User, Depends(get_current_active_user)],
):
    return current_user
