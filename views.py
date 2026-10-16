from flask import Blueprint, abort, current_app, flash, g, redirect, render_template, request, url_for

from . import bookings, catalog, charts

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template(
        "index.html",
        featured=catalog.list_routes(featured=True),
        stats=catalog.site_stats(),
    )


@bp.route("/routes")
def routes():
    difficulty = request.args.get("difficulty")
    if difficulty not in catalog.DIFFICULTIES:
        difficulty = None
    return render_template(
        "routes/list.html",
        routes=catalog.list_routes(difficulty=difficulty),
        counts=catalog.difficulty_counts(),
        active=difficulty,
    )


@bp.route("/routes/<slug>")
def route_detail(slug):
    route = catalog.get_route(slug)
    if route is None:
        abort(404)
    return render_template(
        "routes/detail.html",
        route=route,
        departures=catalog.departures_for(route["id"]),
        profile=charts.elevation_profile(route["profile"]),
        max_participants=current_app.config["MAX_PARTICIPANTS"],
    )


@bp.route("/routes/<slug>/book", methods=("POST",))
def book(slug):
    route = catalog.get_route(slug)
    if route is None:
        abort(404)

    detail_url = url_for("main.route_detail", slug=slug)
    if g.user is None:
        flash("Маршрутқа жазылу үшін аккаунтыңызға кіріңіз.", "info")
        return redirect(url_for("auth.login", next=detail_url))

    departure = catalog.get_departure(request.form.get("departure_id", type=int), route["id"])
    if departure is None:
        flash("Шығу күнін тізімнен таңдаңыз.", "error")
        return redirect(detail_url + "#booking")

    try:
        bookings.create(g.user["id"], departure, request.form.get("participants", type=int))
    except bookings.BookingError as error:
        flash(str(error), "error")
        return redirect(detail_url + "#booking")

    flash(f"Сіз «{route['title']}» маршрутына жазылдыңыз. Толық ақпарат төменде.", "success")
    return redirect(url_for("account.dashboard"))


@bp.route("/guides")
def guides():
    return render_template("guides.html", guides=catalog.list_guides())


@bp.route("/rules")
def rules():
    return render_template("rules.html")
