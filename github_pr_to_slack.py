import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

# .env 파일 로드
env_path = find_dotenv()
load_dotenv(env_path)

# GitHub 설정
GITHUB_TOKEN = os.getenv("PAT_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL") 

LABELS = ["OverDue", "D-0", "D-1", "D-2", "D-3"]
REPOSITORIES = [
    {"owner": "jshan0120", "name": "CleCommonSystems"},
    {"owner": "jshan0120", "name": "CleVisionSystems"},
    {"owner": "HosungLee-CLE", "name": "Mount3DEngine"}
]

def get_prs_with_labels(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {GITHUB_TOKEN}",
               "Accept": "application/vnd.github.v3+json"}
    
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Error: GitHub API 요청 실패 ({response.status_code})")
        print(f"🔍 응답 코드: {response.status_code}")
        print(f"🔍 응답 내용: {response.text}")
        return {"status_code": 200, "message": "GitHub API 요청 성공", "prs": []}

    prs = response.json()
    filtered_prs = [
        pr for pr in prs
        if any(label["name"] in LABELS for label in pr.get("labels", []))
    ]
    
    return {"status_code": 200, "message": "GitHub API 요청 성공", "prs": filtered_prs}

# 라벨이 PR에 포함된 경우 표시
def format_pr_labels(pr):
    labels = [label["name"] for label in pr.get("labels", []) if label["name"] in LABELS]
    if labels:
        return f"[{', '.join(labels)}]"
    return ""

def format_slack_message(prs):
    if not prs:
        return ""

    message = ""
    for pr in prs:
        labels_str = format_pr_labels(pr)
        repo_name = pr['base']['repo']['name']
        message += f"{labels_str} <{pr['html_url']}|{pr['title']}> (#{pr['number']} in {repo_name} repository)\n"

    return message

def get_all_prs():
    all_prs = []
    
    for repo in REPOSITORIES:
        response = get_prs_with_labels(repo["owner"], repo["name"])
        if response["status_code"] == 200:
            message = format_slack_message(response["prs"])
            if len(message) != 0:
                all_prs.append(message)
        else:
            message = "📌 PR Reminder!\nPR 로드 실패"
    
    if all_prs:
        return "📌 PR Reminder!\nReview 대기 중인 PR 목록:\n" + "\n".join(all_prs)
    else:
        return "📌 PR Reminder!\nReview를 기다리는 PR이 없습니다."

def send_to_slack(message):
    payload = {"text": message}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    if response.status_code != 200:
        print(f"❌ Error: Slack 메시지 전송 실패 ({response.status_code})")

def main():
    message = get_all_prs()
    send_to_slack(message)

if __name__ == "__main__":
    main()
