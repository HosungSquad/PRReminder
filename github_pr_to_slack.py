import requests
import json

# GitHub 설정
GITHUB_TOKEN = "your_github_token"
REPO_OWNER = "your_repo_owner"
REPO_NAME = "your_repo_name"
LABELS = ["OverDue", "D-0", "D-1", "D-2", "D-3"]

# Slack 설정
SLACK_WEBHOOK_URL = "your_slack_webhook_url"

def get_open_prs_with_labels():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: GitHub API 요청 실패 ({response.status_code})")
        return []
    
    prs = response.json()
    
    filtered_prs = [
        pr for pr in prs 
        if any(label["name"] in LABELS for label in pr.get("labels", []))
    ]
    
    return filtered_prs

def format_slack_message(prs):
    if not prs:
        return "현재 특정 라벨이 포함된 오픈 PR이 없습니다."

    message = "*📌 특정 라벨이 있는 오픈 PR 목록:*\n"
    for pr in prs:
        message += f"• <{pr['html_url']}|{pr['title']}> (#{pr['number']})\n"

    return message

def send_to_slack(message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print(f"Error: Slack 메시지 전송 실패 ({response.status_code})")

def main():
    prs = get_open_prs_with_labels()
    message = format_slack_message(prs)
    send_to_slack(message)

if __name__ == "__main__":
    main()
