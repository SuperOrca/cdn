from flask import (
    Flask,
    render_template,
    request,
    redirect,
    Blueprint,
    jsonify,
    session,
    url_for,
    send_file,
)
from secrets import compare_digest
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
import random
import string
from io import BytesIO

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cdn.db"


db = SQLAlchemy()
db.init_app(app)

PASSWORD = "admin"


class File(db.Model):
    code: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    mimetype: Mapped[str] = mapped_column(nullable=False)
    data: Mapped[bytes] = mapped_column(nullable=False)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
async def index():
    if request.method == "POST":
        if compare_digest(request.form["password"], PASSWORD):
            session["auth"] = True
            return redirect(url_for("dashboard"))

    if session.get("auth"):
        return redirect(url_for("dashboard"))

    return render_template("index.html")


@app.route("/dashboard", methods=["GET"])
async def dashboard():
    if session.get("auth"):
        return render_template(
            "dashboard.html",
            files=[
                file for file in File.query.with_entities(File.code, File.name).all()
            ],
        )

    return redirect(url_for("index")), 401


@app.route("/<code>", methods=["GET"])
async def get_file(code: str):
    file = File.query.filter(File.code == code).first_or_404()
    return send_file(
        BytesIO(file.data), mimetype=file.mimetype, download_name=file.name
    )


api = Blueprint("api", __name__)


def generate_code():
    return "".join(random.choice(string.ascii_uppercase) for _ in range(6))


@api.route("/add", methods=["POST"])
async def add_file():
    if session.get("auth"):
        file = request.files["file"]

        code = generate_code()
        while len(File.query.filter(File.code == code).all()) > 0:
            code = generate_code()

        db.session.add(
            File(
                code=code,
                name=file.filename,
                mimetype=file.mimetype,
                data=file.stream.read(),
            )
        )
        db.session.commit()

        file.close()

        return redirect(url_for("dashboard"))

    return redirect(url_for("index"))


@api.route("/remove", methods=["POST"])
async def remove_file():
    if session.get("auth"):
        data = request.get_json()

        file = File.query.filter(File.code == data.get("code")).first_or_404()
        db.session.delete(file)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return redirect(url_for("index"))


app.register_blueprint(api, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=True)
