import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db


def get_by_id(user_id):
    return get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def create(full_name, email, phone, password):
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO users (full_name, email, phone, password_hash) VALUES (?, ?, ?, ?)",
            (full_name, email, phone, generate_password_hash(password)),
        )
        db.commit()  # <--- МІНЕ, ОСЫ ЖОЛДЫ ҚОСУ КЕРЕК!
    except sqlite3.IntegrityError:
        db.rollback()
        return None
    return cursor.lastrowid


def authenticate(email, password):
    user = get_by_email(email)
    if user is None or not check_password_hash(user["password_hash"], password):
        return None
    return user
