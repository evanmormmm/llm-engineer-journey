from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import String, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)


# ==================== 数据库配置 ====================

DATABASE_URL = "sqlite:///./learning.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# ==================== SQLAlchemy 数据表 ====================


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )


Base.metadata.create_all(engine)


# ==================== Pydantic 数据模型 ====================


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=3, max_length=100)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str


# ==================== 数据库会话依赖 ====================


def get_db() -> Generator[Session]:
    with SessionLocal() as db:
        yield db


DbSession = Annotated[Session, Depends(get_db)]


# ==================== FastAPI ====================

app = FastAPI(title="用户 CRUD 练习")


# Create：新增用户
@app.post(
    "/users",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    data: UserCreate,
    db: DbSession,
) -> User:
    user = User(
        name=data.name,
        email=data.email,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="该邮箱已经存在",
        ) from error

    db.refresh(user)
    return user


# Read：查询全部用户
@app.get("/users", response_model=list[UserRead])
def list_users(db: DbSession) -> list[User]:
    statement = select(User).order_by(User.id)
    users = db.scalars(statement).all()

    return list(users)


# Read：根据 ID 查询用户
@app.get("/users/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: DbSession,
) -> User:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    return user


# Update：修改用户
@app.put("/users/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    data: UserCreate,
    db: DbSession,
) -> User:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    user.name = data.name
    user.email = data.email

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="该邮箱已经存在",
        ) from error

    db.refresh(user)
    return user


# Delete：删除用户
@app.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: int,
    db: DbSession,
) -> Response:
    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="用户不存在",
        )

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
