import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
PASSWORD_MIN_LENGTH = 8


def normalize_phone(raw):
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits[0] in "78":
        digits = digits[1:]
    if len(digits) != 10:
        return None
    return "+7" + digits


def is_strong_password(password):
    return (
        len(password) >= PASSWORD_MIN_LENGTH
        and any(char.isalpha() for char in password)
        and any(char.isdigit() for char in password)
    )


def validate_registration(form):
    data = {
        "full_name": " ".join(form.get("full_name", "").split()),
        "email": form.get("email", "").strip().lower(),
        "phone": form.get("phone", "").strip(),
        "password": form.get("password", ""),
        "password_confirm": form.get("password_confirm", ""),
        "agree": form.get("agree") == "on",
    }
    errors = {}

    if not 2 <= len(data["full_name"]) <= 60:
        errors["full_name"] = "Аты-жөніңізді жазыңыз (2–60 таңба)."

    if len(data["email"]) > 120 or not EMAIL_PATTERN.match(data["email"]):
        errors["email"] = "Email мекенжайын дұрыс енгізіңіз, мысалы: aigerim@mail.kz"

    phone = normalize_phone(data["phone"])
    if phone is None:
        errors["phone"] = "Телефон нөмірін +7 700 123 45 67 форматында енгізіңіз."
    else:
        data["phone"] = phone

    if not is_strong_password(data["password"]):
        errors["password"] = "Құпия сөз кемінде 8 таңбадан тұрып, әріп пен цифрды қамтуы керек."
    elif data["password"] != data["password_confirm"]:
        errors["password_confirm"] = "Құпия сөздер сәйкес келмейді."

    if not data["agree"]:
        errors["agree"] = "Тіркелу үшін қатысу ережелерімен келісу қажет."

    return data, errors


def validate_login(form):
    data = {
        "email": form.get("email", "").strip().lower(),
        "password": form.get("password", ""),
    }
    if not data["email"] or not data["password"]:
        return data, "Email мен құпия сөзді енгізіңіз."
    return data, None
