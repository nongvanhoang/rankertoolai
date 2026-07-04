import requests
import os
from datetime import datetime
from content_generator import generate_content
from database import log_post, already_posted, has_recent_error

HASHNODE_API = "https://gql.hashnode.com"

def post(tool):
    if already_posted("hashnode", tool["slug"], days=30):
        print(f"[Hashnode] Already posted {tool['name']} this month, skipping")
        return

    if has_recent_error("hashnode", tool["slug"], hours=48):
        print(f"[Hashnode] Recent error for {tool['name']}, cooling down 48h")
        return

    token = os.getenv("HASHNODE_ACCESS_TOKEN", "").strip()
    publication_id = os.getenv("HASHNODE_PUBLICATION_ID", "").strip()

    if not token or not publication_id:
        print("[Hashnode] Missing HASHNODE_ACCESS_TOKEN or HASHNODE_PUBLICATION_ID — skipping")
        return

    try:
        content = generate_content("hashnode", tool)
        lines = content.strip().split("\n")
        title = lines[0].strip().lstrip("#").strip()
        body = "\n".join(lines[1:]).strip()

        # Add month/year suffix to avoid duplicate title errors
        month_year = datetime.now().strftime("%b %Y")
        if month_year not in title:
            title = f"{title} ({month_year})"

        query = """
        mutation PublishPost($input: PublishPostInput!) {
          publishPost(input: $input) {
            post { id url title }
          }
        }
        """

        variables = {
            "input": {
                "title": title,
                "contentMarkdown": body,
                "publicationId": publication_id,
                "tags": []
            }
        }

        # Hashnode PAT: Authorization header without Bearer prefix
        headers = {
            "Authorization": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        r = requests.post(HASHNODE_API, json={"query": query, "variables": variables}, headers=headers)

        # Detect HTML response (Cloudflare block = missing/invalid token)
        content_type = r.headers.get("Content-Type", "")
        if "text/html" in content_type:
            raise ValueError(f"Hashnode returned HTML — token may be invalid or expired. Status: {r.status_code}")

        r.raise_for_status()
        data = r.json()

        # Check for GraphQL-level errors
        gql_errors = data.get("errors")
        if gql_errors:
            raise ValueError(f"GraphQL error: {gql_errors[0].get('message', gql_errors)}")

        post_data = data.get("data", {}).get("publishPost", {}).get("post", {})
        url = post_data.get("url", "")
        post_id = post_data.get("id", "")

        log_post("hashnode", tool["slug"], "article", post_id, url)
        print(f"[Hashnode] Published: {url}")
        return url

    except Exception as e:
        log_post("hashnode", tool["slug"], "article", status="error", error=str(e))
        print(f"[Hashnode] Error: {e}")
        return None
