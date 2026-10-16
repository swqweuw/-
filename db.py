import sqlite3
from pathlib import Path

import click
from flask import current_app, g

from . import seed


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
    db.executescript(schema)
    seed.populate(db)
    db.commit()


def ensure_database():
    table = get_db().execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'routes'"
    ).fetchone()
    if table is None:
        init_db()


@click.command("init-db")
def init_db_command():
    init_db()
    click.echo("Derekqor qaita quryldy.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
