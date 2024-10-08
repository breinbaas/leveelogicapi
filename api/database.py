import sqlite3
from enum import IntEnum
from pydantic import BaseModel
from passlib.hash import pbkdf2_sha256

DATABASE_NAME = "api.db"


class UserRole(IntEnum):
    VIEW = 0
    EDIT = 1
    ADMIN = 2


class User(BaseModel):
    name: str
    email: str
    role: UserRole = UserRole.VIEW
    disabled: bool = False


USERROLES = {
    UserRole.VIEW: "view",
    UserRole.EDIT: "edit",
    UserRole.ADMIN: "admin",
}


def create_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute(
        """CREATE TABLE if not exists Users
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,                
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role CHAR(10) NOT NULL,
                disabled BOOL NOT NULL
            );
        """
    )
    conn.close()


def add_user(user: User, password: str, role: UserRole = UserRole.VIEW):
    hashed_password = pbkdf2_sha256.hash(password)
    sql = f"INSERT INTO Users (name, email, password, role, disabled) VALUES ('{user.name}', '{user.email}', '{hashed_password}', '{USERROLES[role]}', 0)"
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute(sql)
    conn.commit()
    conn.close()


def get_and_validate_user(email: str, password: str):
    sql = f"SELECT name, password, role, disabled from Users WHERE email='{email}' LIMIT 1"
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.execute(sql)
    for row in cursor:
        hash = pbkdf2_sha256.hash(password)
        if pbkdf2_sha256.verify(password, hash):
            if row[2] == "view":
                role = UserRole.VIEW
            elif row[2] == "edit":
                role = UserRole.EDIT
            elif row[2] == "admin":
                role = UserRole.ADMIN
            else:
                raise ValueError(f"Invalid user role '{row[2]}' found")

            return User(name=row[0], email=email, role=role, disabled=row[3] == 1)
        else:
            return None


def get_user_by_name(email: str):
    sql = f"SELECT name, password, role, disabled from Users WHERE email='{email}' LIMIT 1"
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.execute(sql)
    for row in cursor:
        if row[2] == "view":
            role = UserRole.VIEW
        elif row[2] == "edit":
            role = UserRole.EDIT
        elif row[2] == "admin":
            role = UserRole.ADMIN
        else:
            raise ValueError(f"Invalid user role '{row[2]}' found")

        return User(name=row[0], email=email, role=role, disabled=row[3] == 1)
    return None
