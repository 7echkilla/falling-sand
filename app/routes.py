import time

from flask import Blueprint, request, send_file, jsonify, redirect, render_template, Response
from app import config
from app.github import fetch_contributions, get_username, code_to_token
from app.gif import generate_gif_bytes
from app.db import get_access_token, save_user
from app.auth import generate_signed_token, verify_signed_token

main = Blueprint("main", __name__)  # Organise routes into a module

cache = {}
CACHE_TTL = 300 # 5 minutes

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

    if (not authorisation_code):
        return jsonify({"error": "Missing code"}), 400
    
    # Exchange code for access token
    access_token = code_to_token(
        authorisation_code,
        config.CLIENT_ID,
        config.CLIENT_SECRET
    )

    # Store user to avoid recurring login
    username = get_username(access_token)
    save_user(username, access_token)

    signed_token = generate_signed_token(username)

    return render_template(
        "success.html",
        username=username,
        url_root=request.url_root,
        token=signed_token
    )

@main.route("/gif")
def gif():
    # Fetch parameters from: /gif?username=abc&key=123
    username = request.args.get("username")
    token = request.args.get("token")

    if (not username or not token):
        return jsonify({"error": "Missing parameters"}), 400

    # Prevent abuse of API by unauthorised users
    if (not verify_signed_token(username, token)):
        return jsonify({"error": "Unauthorised"}), 403

    # Serve from cache (if available)
    if (username in cache):
        gif_bytes, timestamp = cache[username]
        if (time.time() - timestamp < CACHE_TTL):
            return Response(gif_bytes, mimetype="image/gif")
        
    # Reject non-logged in users
    access_token = get_access_token(username)
    if (not access_token):
        return jsonify({"error": "User not logged in"}), 401

    # Slow part on occasional runs
    days = fetch_contributions(username, access_token)
    gif_bytes = generate_gif_bytes(days)
    cache[username] = (gif_bytes, time.time())  # Store in cache

    return Response(gif_bytes, mimetype="image/gif")