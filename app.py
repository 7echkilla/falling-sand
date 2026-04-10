import io
import os
import requests

# from dotenv import load_dotenv
# load_dotenv("config.env")

from flask import Flask, redirect, request, send_from_directory, send_file

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
USERS = {}  # Store username as ID; Upgrade to SQLite

app = Flask(__name__)

# Home page
@app.route("/")
def home():
    return '<a href="/login">Login with GitHub</a>'

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

# Redirect to GitHub for OAuth
@app.route("/login")
def login():
    redirect_uri = request.url_root + "callback"
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&scope=read:user"
        f"&redirect_uri={redirect_uri}"
    )

    return redirect(auth_url)

def get_username(access_token):
    url = "https://api.github.com/graphql"
    headers={"Authorization": f"Bearer {access_token}"}
    query = """ {
        viewer {
            login 
        }
    } """

    response = requests.post(url=url, json={"query": query}, headers=headers).json()
    
    return response["data"]["viewer"]["login"]

# GitHub redirects
@app.route("/callback")
def callback():
    code = request.args.get("code")
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code
    }

    # Exchange code for token
    response = requests.post(url=url, json=payload, headers=headers).json()
    
    if "access_token" not in response:
        return f"OAuth failed: {response}", 400
    access_token = response.get("access_token")

    username = get_username(access_token)
    USERS[username] = access_token
    
    return f"""
    <h2>You're all set!</h2>
    <pre>
    ![My Contributions]({request.url_root}gif?username={username})
    </pre>
    """

@app.route("/gif")
def dynamic_gif():
    username = request.args.get("username")

    if not username or username not in USERS:
        return "Invalid username", 400

    token = USERS[username]

    url = "https://api.github.com/graphql"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "falling-sand"
    }
    
    query = """
        query {
            viewer {
                contributionsCollection {
                    contributionCalendar {
                        weeks {
                            contributionDays {
                                date
                                contributionCount
                            }
                        }
                    }
                }
            }
        }
    """

    response = requests.post(url=url, json={"query": query}, headers=headers)

    if (response.status_code != 200):
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    try:
        weeks = data['data']['viewer']['contributionsCollection']['contributionCalendar']['weeks']
    except KeyError:
        raise Exception("Unexpected API response structure")
    
    # Flatten with list comprehension (faster than nested loops)
    days = [
        {"date": day['date'], "count": day['contributionCount']}
        for week in weeks
        for day in week['contributionDays']
    ]

    # Generate GIF in memory
    gif_bytes = generate_gif_bytes(days)

    response = send_file(gif_bytes, mimetype="image/gif")
    response.headers["Cache-Control"] = "public, max-age=300"
    response.headers["Content-Type"] = "image/gif"
    return response

from PIL import Image, ImageDraw
import io

def generate_gif_bytes(days):
    frames = []

    width = 53 * 12
    height = 7 * 12

    for i in range(len(days)):
        img = Image.new("RGB", (width, height), "#ebedf0")
        draw = ImageDraw.Draw(img)

        for j in range(i + 1):
            x = (j // 7) * 12
            y = (j % 7) * 12
            count = days[j]["count"]

            # GitHub-style color levels
            levels = [0, 1, 3, 6, 10]
            colors = [
                (235,237,240),
                (198,228,139),
                (123,201,111),
                (35,154,59),
                (25,97,39)
            ]

            color = colors[0]
            for k in range(1, len(levels)):
                if count >= levels[k]:
                    color = colors[k]

            draw.rectangle([x, y, x+12, y+12], fill=color)

        frames.append(img)

    gif_io = io.BytesIO()

    frames[0].save(
        gif_io,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )

    gif_io.seek(0)
    return gif_io

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)