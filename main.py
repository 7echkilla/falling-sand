import requests
import pandas as pd

def fetch_contributions(username, token):
    """
    Fetches user contribution details over GitHub's GraphQL API and passes returns contributions dataframe
    """

    url = "https://api.github.com/graphql"
    variables = {"username": username}
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "falling-sand"
    }
    
    query = """
        query getContributions($username: String!) {
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

    payload = {"query": query, "variables": variables}
    response = requests.post(url=url, json=payload, headers=headers)

    if (response.status_code != 200):
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    try:
        weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
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

import os
import tempfile
import tqdm
import matplotlib.pyplot as plt
import imageio.v2 as imageio

def generate_gif(dataframe, output_file="falling_sand.gif"):
    """
    Generate GIFs out of provided dataframe with structure (date, count)
    """
    
    dataframe = dataframe.sort_values('date')
    max_count = dataframe['count'].max()
    images = []

    with tempfile.TemporaryDirectory() as temporary_dirname:
        # Display progress bar for frames generation
        for i in tqdm.tqdm(range(1, len(dataframe) + 1), desc="Generating frames"):
            figure, axes = plt.subplots(figsize=(10, 3))
            subset = dataframe.iloc[:i]
            axes.bar(subset['date'], subset['count'], color='green')
            axes.set_ylim(0, max_count + 1)
            axes.set_xlabel("Date")
            axes.set_ylabel("Contributions")
            axes.set_title("GitHub Contributions over Time")
            figure.tight_layout()

            # Save frame to a temporary file
            frame_path = os.path.join(temporary_dirname, f"frame_{i}.png")
            plt.savefig(frame_path)
            plt.close(figure)
            images.append(imageio.imread(frame_path))

    # Create GIF
    imageio.mimsave(output_file, images, duration=0.1)

if __name__ == "__main__":
    username = input("Enter your GitHub username: ")
    token = input("Enter you GitHub Personal Access Token: ")

    dataframe = fetch_contributions(username, token)
    print(dataframe)
    generate_gif(dataframe)