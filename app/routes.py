from flask import Blueprint, request, send_file, jsonify, redirect, render_template
from app import config
from app.github import fetch_contributions, get_username, code_to_token
from app.gif import generate_gif_bytes
from app.db import get_token, save_user

main = Blueprint("main", __name__)  # Organise routes into a module

@main.route("/")
def home():
    return render_template("home.html")

@main.route("/login")
def login():
    redirect_uri = request.url_root + "callback"    # https://falling-sand.onrender.com/callback

    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={config.CLIENT_ID}"            # Indentifies app to GitHub
        "&scope=read:user"                          # Permission to read user information
        f"&redirect_uri={redirect_uri}"             # Post login redirect
    )

    return redirect(url)

@main.route("/callback")
def callback():
    authorisation_code = request.args.get("code")   # Temporary code sent by GitHub as proof

    # Exchange code for access token
    access_token = code_to_token(
        authorisation_code,
        config.CLIENT_ID,
        config.CLIENT_SECRET
    )

    # Store user to avoid recurring login
    username = get_username(access_token)
    save_user(username, access_token)

    return render_template("success.html", username=username, url_root=request.url_root)

@main.route("/gif")
def gif():
    # Fetch parameters from: /gif?username=abc&key=123
    username = request.args.get("username")
    key = request.args.get("key")

    # Prevent abuse of API by unauthorised users
    if (key != config.GIF_SECRET):
        return jsonify({"error": "Unauthorized"}), 403

    # Reject non-logged in users
    access_token = get_token(username)
    if (not access_token):
        return jsonify({"error": "User not logged in"}), 401

    days = fetch_contributions(username, access_token)
    gif_bytes = generate_gif_bytes(days)

    return send_file(gif_bytes, mimetype="image/gif")