# discord_points_site/app.py

from flask import Flask, redirect, request, session, render_template
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
REDIRECT_URI = "https://your-render-url.onrender.com/callback"  # Replace this after deployment
API_BASE_URL = "https://discord.com/api"
OAUTH_SCOPE = "identify"

# Dummy database for storing user points
user_points = {
    "1399515777119551518": 1200  # Your Discord ID with starting points
}

@app.route("/")
def index():
    user = session.get("user")
    points = user_points.get(user["id"], 0) if user else None
    return render_template("index.html", user=user, points=points)

@app.route("/login")
def login():
    return redirect(
        f"{API_BASE_URL}/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={OAUTH_SCOPE}"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": OAUTH_SCOPE,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(f"{API_BASE_URL}/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    credentials = r.json()

    user_res = requests.get(
        f"{API_BASE_URL}/users/@me",
        headers={"Authorization": f"Bearer {credentials['access_token']}"}
    )
    user_res.raise_for_status()
    session["user"] = user_res.json()

    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or fallback
    app.run(host="0.0.0.0", port=port)
