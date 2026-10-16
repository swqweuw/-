import functools
from urllib.parse import urlsplit

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from . import users
from .validators import validate_login, validate_registration

bp = Blueprint("auth", __name__)

DUPLICATE_EMAIL = "Бұл email мекенжайымен аккаунт бұрыннан тіркелген."


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = users.get_by_id(user_id) if user_id is not None else None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Бұл бетті көру үшін аккаунтыңызға кіріңіз.", "info")
            target = request.full_path.rstrip("?") if request.method == "GET" else None
            return redirect(url_for("auth.login", next=target))
        return view(**kwargs)

    return wrapped_view


def safe_next(target):
    if not target or not target.startswith("/") or target.startswith(("//", "/\\")):
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return None
    return target


@bp.route("/register", methods=("GET", "POST"))
def register():
    if g.user is not None:
        return redirect(url_for("account.dashboard"))

    form, errors = {}, {}
    if request.method == "POST":
        form, errors = validate_registration(request.form)
        if not errors and users.get_by_email(form["email"]) is not None:
            errors["email"] = DUPLICATE_EMAIL
        if not errors:
            user_id = users.create(form["full_name"], form["email"], form["phone"], form["password"])
            if user_id is not None:
                session["prefill_email"] = form["email"]
                flash("Тіркелу сәтті аяқталды. Енді аккаунтыңызға кіріңіз.", "success")
                return redirect(url_for("auth.login"))
            errors["email"] = DUPLICATE_EMAIL

    return render_template("auth/register.html", form=form, errors=errors)


@bp.route("/login", methods=("GET", "POST"))
def login():
    next_url = safe_next(request.values.get("next"))
    if g.user is not None:
        return redirect(next_url or url_for("account.dashboard"))

    form = {"email": session.pop("prefill_email", "")}
    error = None
    if request.method == "POST":
        form, error = validate_login(request.form)
        if error is None:
            user = users.authenticate(form["email"], form["password"])
            
            print("ТЕРБЕУГЕ КЕЛГЕН USER:", user)
            print("ЕНГІЗГЕН ПАРОЛЬ:", form["password"])
            
            if user is None:
                error = "Email немесе құпия сөз қате."
            else:
                session.clear()
                session["user_id"] = user["id"]
                flash("Аккаунтыңызға сәтті кірдіңіз.", "success")
                return redirect(next_url or url_for("account.dashboard"))

    return render_template("auth/login.html", form=form, error=error, next_url=next_url)

@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    flash("Сіз аккаунттан шықтыңыз.", "info")
    return redirect(url_for("main.index"))
