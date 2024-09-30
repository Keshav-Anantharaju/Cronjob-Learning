import requests
import json
from datetime import datetime
import os

# GitHub configuration
GITHUB_TOKEN = os.getenv('MY_SECRET')
REPO_OWNER = "InspectHOA"
REPO_NAME = "inspecthoa"

# GitHub API URL
API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"

# Headers for the request
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}



def fetch_pull_requests():
    """Fetches all open pull requests from the repository."""
    all_prs = []
    page = 1
    
    while True:
        response = requests.get(API_URL, headers=headers, params={"state": "open", "per_page": 100, "page": page})
        
        if response.status_code != 200:
            print(f"Error fetching pull requests: {response.json()}")
            return []

        prs = response.json()
        if not prs:  
            break

        all_prs.extend(prs)  
        print(f"Fetched {len(prs)} pull requests from page {page}")
        page += 1  

    
    with open("prs.json", "w") as f:
        json.dump(all_prs, f, indent=4)
    
    print(f"Total pull requests fetched: {len(all_prs)}")
    return all_prs



def fetch_reviews(pr_number):
    """Fetches reviews for a specific pull request."""
    reviews_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
    response = requests.get(reviews_url, headers=headers)

    if response.status_code != 200:
        print(f"Error fetching reviews for PR {pr_number}: {response.json()}")
        return []

    return response.json()





def extract_completed_reviews(prs):
    """Extracts completed reviews from pull requests."""
    completed_reviews = {}
    today = datetime.utcnow()
    today = datetime.combine(today, datetime.min.time())

    for pr in prs:
        reviews = fetch_reviews(pr["number"])
        for review in reviews:
            if review["state"] == "APPROVED":
                submitted_at = datetime.strptime(review["submitted_at"], "%Y-%m-%dT%H:%M:%SZ")
                if submitted_at > today:  # Compare with today's date
                    pr_key = pr["number"]
                    if pr_key not in completed_reviews:
                        completed_reviews[pr_key] = []
                    completed_reviews[pr_key].append(
                        {
                            "reviewer": review["user"]["login"],
                            "timestamp": review["submitted_at"],
                            "pr_title": pr["title"],
                            "pr_url": pr["html_url"],
                        }
                    )

    return completed_reviews



def save_reviews_to_file(reviews):
    """Saves the extracted reviews to a JSON file."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    with open(f"pr_reviews_{timestamp}.json", "w") as f:
        json.dump(reviews, f, indent=4)


def main():
    prs = fetch_pull_requests()
    completed_reviews = extract_completed_reviews(prs)

    if completed_reviews:
        save_reviews_to_file(completed_reviews)
        print(f"Saved {len(completed_reviews)} completed reviews to file.")
    else:
        print("No completed reviews found.")


if __name__ == "__main__":
    main()

