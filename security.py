import hmac
import secrets

from flask import abort, current_app, request, session

CSRF_FIELD = "csrf_token"
CSRF_MESSAGE = "Форманың қорғаныс белгісі (CSRF) жарамсыз немесе ескірген. Бетті жаңартып, әрекетті қайталаңыз."


def get_csrf_token():
    token = session.get(CSRF_FIELD)
    if token is None:
        token = secrets.token_urlsafe(32)
        session[CSRF_FIELD] = token
    return token


def verify_csrf():
    if not current_app.config.get("CSRF_ENABLED", True):
        return
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return
    sent = request.form.get(CSRF_FIELD, "")
    expected = session.get(CSRF_FIELD, "")
    if not expected or not hmac.compare_digest(sent, expected):
        abort(400, description=CSRF_MESSAGE)


def init_app(app):
    app.before_request(verify_csrf)
    app.jinja_env.globals["csrf_token"] = get_csrf_token
