from flask import Flask, render_template, request, redirect, Blueprint, jsonify, session, url_for
from secrets import compare_digest
import os
from models import File

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(32)

PASSWORD = "imsilly74"

@app.route("/", methods=["GET", "POST"])
async def index():
    if request.method == "POST":
        if compare_digest(request.form["password"], PASSWORD):
            session["auth"] = True
            return redirect(url_for("dashboard"))
        
    return render_template("index.html")

@app.route("/dashboard", methods=["GET"])
async def dashboard():
    if session.get("auth"):
        return render_template("dashboard.html")

    return redirect(url_for("index")), 401

@app.route("/<code>", methods=["GET"])
async def get_file(code: str):
    file = File.query.filter_by(code=code).first_or_404()
    return file

api = Blueprint("api", __name__)

@api.route("/files")
async def get_files():
    if session.get("auth"):
        return jsonify(File.query.all())

    return jsonify({"success": False})

@api.route("/add")
async def add_file():
    return jsonify({"success": False})

@api.route("/remove")
async def remove_file():
    return jsonify({"success": False})

app.register_blueprint(api, url_prefix="/api")

if __name__ == '__main__':
    app.run(debug=True)
