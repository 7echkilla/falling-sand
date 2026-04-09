import requests
import pandas as pd
from datetime import datetime

def fetch_contributions(username, token):
    """
    Fetches user contribution details over GitHub's GraphQL API and passes returns contributions dataframe
    """

    url = "https://api.github.com/graphql"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "falling-sand"
    }

    variables = {"username": username}
    query = """
        query($username: String!) {
            user(login: $username) {
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

    response = requests.post(url=url, json={"query": query, "variables": variables}, headers=headers)

    if response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    payload = response.json()
    
    try:
        weeks = payload['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
    except KeyError:
        raise Exception("Unexpected API response structure")
    
    # Flatten with list comprehension (faster than nested loops)
    days = [
        {"date": day['date'], "count": day['contributionCount']}
        for week in weeks
        for day in week['contributionDays']
    ]
    
    dataframe = pd.DataFrame(days)
    dataframe['date'] = pd.to_datetime(dataframe['date'])
    
    return dataframe

if __name__ == "__main__":
    username = input("Enter your GitHub username: ")
    token = input("Enter you GitHub Personal Access Token: ")

    dataframe = fetch_contributions(username, token)
    print(dataframe)