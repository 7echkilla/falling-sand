import requests

def code_to_token(authorisation_code, client_id, client_secret):
    """
    Convert temporary login code to usable API token 
    """

    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorisation_code
    }

    response = requests.post(url=url, json=payload, headers=headers).json()

    if ("access_token" not in response):
        raise Exception(f"OAuth failed: {response}")
    access_token = response["access_token"]

    return access_token

def get_username(token):
    """
    Fetch username using authorisation token
    """

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = """ { 
        viewer { 
            login
        } 
    } """

    response = requests.post(url=url, json={"query": query}, headers=headers).json()
    username = response["data"]["viewer"]["login"]
    
    return username 

def fetch_contributions(username, token):
    """
    Request user contributions via GitHub's GraphQL API
    """

    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    query = f"""
        query {{
            user(login: "{username}") {{
                contributionsCollection {{
                contributionCalendar {{
                    weeks {{
                    contributionDays {{
                        date
                        contributionCount
                    }}
                    }}
                }}
                }}
            }}
        }}
    """

    response = requests.post(url=url, json={"query": query}, headers=headers)
    if (response.status_code != 200):
        raise Exception("GitHub API request failed")
    
    response = response.json()

    try:
        weeks = response["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    except KeyError:
        raise Exception("Invalid GitHub username or API response")

    # Flatten data as list comprehension (faster than nested for loops)
    days = [
        {"date": day["date"], "count": day["contributionCount"]}
        for week in weeks
        for day in week["contributionDays"]
    ]

    return days