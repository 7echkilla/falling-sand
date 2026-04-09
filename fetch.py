import requests
import pandas as pd
from datetime import datetime

def fetch_contributions(username, token):
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {token}"}
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
    variables = {"username": username}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    data = response.json()

    days = []
    for week in data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']:
        for day in week['contributionDays']:
            days.append({"date": day['date'], "count": day['contributionCount']})

    df = pd.DataFrame(days)
    df['date'] = pd.to_datetime(df['date'])

    return df

if __name__ == "__main__":
    username = input("Enter your GitHub username: ")
    token = input("Enter you GitHub Personal Access Token: ")

    df = fetch_contributions(username, token)
    print(df)   