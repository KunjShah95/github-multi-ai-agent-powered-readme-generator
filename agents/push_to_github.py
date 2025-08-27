import base64
import requests
from core.a2a_protocol import A2AMessage

class GitHubPushAgent:

    # --- AGENT ROLE PROMPT ---
    # You are the GitHubPushAgent. Your role is to:
    # 1. Push the generated README to the target GitHub repository using the GitHub API.
    # 2. Handle authentication, file existence checks, and commit messages.
    # 3. Support updating existing files or creating new ones as needed.
    # 4. Provide clear status messages and error handling for push operations.
    # 5. Optionally support branch selection, PR creation, and commit history tracking.
    # 6. Optionally notify users or trigger CI/CD after push.
    #
    # --- FEATURE SUGGESTIONS ---
    # - Add support for pushing to branches and opening pull requests.
    # - Integrate with GitHub Actions to trigger workflows after push.
    # - Support for custom commit messages and author attribution.
    # - Add retry logic and rate limit handling for API calls.
    # - Provide a push log and status dashboard.
    # - Optionally support pushing other documentation files.
    #
    def __init__(self, github_token):
        self.token = github_token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def get_repo_file_sha(self, owner, repo, path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("sha")
        return None  # File does not exist yet

    def push_readme(self, github_url, readme_text, commit_message="🤖 Auto-generated README"):
        try:
            parts = github_url.replace("https://github.com/", "").split("/")
            owner, repo = parts[0], parts[1]

            path = "README.md"
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            sha = self.get_repo_file_sha(owner, repo, path)

            data = {
                "message": commit_message,
                "content": base64.b64encode(readme_text.encode("utf-8")).decode("utf-8"),
                "branch": "main"  # or "master"
            }
            if sha:
                data["sha"] = sha

            response = requests.put(url, headers=self.headers, json=data)

            if response.status_code in [200, 201]:
                return f"✅ README pushed to GitHub: {github_url}"
            else:
                return f"❌ GitHub push failed: {response.status_code} - {response.text}"
        except Exception as e:
            return f"❌ Exception during GitHub push: {e}"

    def run(self, github_url, message: A2AMessage):
        if message.message_type != "final_readme":
            return A2AMessage(
                from_agent="GitHubPushAgent",
                to_agent="UI",
                message_type="error",
                content="Expected final_readme message."
            )

        result = self.push_readme(github_url, message.content)
        return A2AMessage(
            from_agent="GitHubPushAgent",
            to_agent="UI",
            message_type="github_push_status",
            content=result
        )
