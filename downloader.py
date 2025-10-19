import requests
import zipfile
import io
import os

def download_github_repo(repo_url, dest_folder):
    """
    Downloads a GitHub repo ZIP and extracts it.
    Works with any default branch (main/master/custom).
    """

    # Normalize the URL
    repo_url = repo_url.strip().rstrip("/")

    # Extract owner/repo name
    if "github.com" not in repo_url:
        raise Exception("Invalid GitHub URL. Example: https://github.com/username/repo")

    parts = repo_url.split("github.com/")[-1].split("/")
    if len(parts) < 2:
        raise Exception("Invalid GitHub repo URL. It should look like https://github.com/user/repo")

    owner, repo = parts[0], parts[1]

    # Get default branch from GitHub API
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"Failed to access repository API. ({response.status_code})")

    data = response.json()
    default_branch = data.get("default_branch", "main")

    # Build the ZIP URL using the correct branch
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{default_branch}.zip"

    print(f"Downloading ZIP from: {zip_url}")

    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download ZIP from {zip_url}")

    zip_data = zipfile.ZipFile(io.BytesIO(response.content))

    extract_path = os.path.join(dest_folder, repo)
    os.makedirs(extract_path, exist_ok=True)

    zip_data.extractall(extract_path)
    zip_data.close()

    return extract_path
