import requests
import json
import urllib
import os

def main(SLACK_WEBHOOK):
    open_prs={
        'Needs review' : 0,
        'Approved' : 0,
        'Change required' : 0
    }

    # Fetch repository status data from GitHub API
    repo_loc = os.environ.get("GITHUB_REPOSITORY")
    github_token = os.environ.get("GITHUB_TOKEN")

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    pulls_url = f"https://api.github.com/repos/{repo_loc}/pulls"

    response = requests.get(pulls_url, headers=headers)
    data = response.json()
    if response.status_code == 200:
        pull_requests = response.json()
        # Iterate over the pull requests
        for pr in pull_requests:
            if not pr["user"]["type"] == "Bot":
                response = requests.get(f"{pulls_url}/{pr['number']}/reviews", headers=headers)
                data = response.json()
                if response.status_code == 200:
                    reviews = response.json()
                    # Iterate over the reviews
                    for review in reviews:
                        if review["state"] == "APPROVED":
                            open_prs['Approved'] += 1
                        elif review["state"] == "CHANGES_REQUESTED":
                            open_prs['Change required'] += 1
                        else:
                            open_prs['Needs review'] += 1
    else:
        print(f"Failed to retrieve pull requests (Status code: {response.status_code})")
    chart_settings = {
        "type": "outlabeledPie",
        "data": {
            "labels": list(open_prs.keys()),
            "datasets": [
                {
                    "backgroundColor": ["#FF3784", "#36A2EB", "#4BC0C0"],
                    "data": list(open_prs.values())
                }
            ]
        },
        "options": {
            "plugins": {
                "legend": False,
                "outlabels": {
                    "text": "%l : %v",
                    "color": "white",
                    "stretch": 35,
                    "font": {
                        "minSize": 12,
                        "maxSize": 18
                    }
                }
            }
        }
    }

    chart_settings_json = json.dumps(chart_settings)
    encoded_chart_settings = urllib.parse.quote(chart_settings_json)
    # Construct the URL with the encoded chart settings
    img_url = f"https://quickchart.io/chart?c={encoded_chart_settings}"
    hook_url = SLACK_WEBHOOK
    payload = {
        # "channel": channel,
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Repo Status Graph"
                }
            },
            {
                "type": "image",
                "image_url": img_url,
                "alt_text": "Repo Status Graph"
            }
        ]
    }
    response = requests.post(hook_url, json=payload)
    if response.status_code == 200:
        print("Repo status graph sent successfully to Slack!")
    else:
        print("Failed to send repo status graph to Slack.")
        print("Response:", response.text)

if __name__ == "__main__":
    main(os.environ.get("SLACK_WEBHOOK"))