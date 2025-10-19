import requests
import zipfile
import io
import os

def download_github_repo(repo_url, dest_folder):
    """
    Downloads a GitHub repo ZIP and extracts it.
    Detects default branch dynamically.
    Checks for 'installerready.exe' or 'installerready.bat' after download.
    """

    repo_url = repo_url.strip().rstrip("/")

    if "github.com" not in repo_url:
        raise Exception("Invalid GitHub URL. Example: https://github.com/username/repo")

    parts = repo_url.split("github.com/")[-1].split("/")
    if len(parts) < 2:
        raise Exception("Invalid GitHub repo URL. It should look like https://github.com/user/repo")

    owner, repo = parts[0], parts[1]

    # --- Get the default branch dynamically ---
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"Failed to access GitHub API ({response.status_code}).")
    data = response.json()
    default_branch = data.get("default_branch", "main")

    # --- Download the ZIP ---
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{default_branch}.zip"
    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download ZIP from {zip_url}")

    # --- Extract ZIP contents ---
    zip_data = zipfile.ZipFile(io.BytesIO(response.content))
    extract_path = os.path.join(dest_folder, repo)
    os.makedirs(extract_path, exist_ok=True)
    zip_data.extractall(extract_path)
    zip_data.close()

    # --- Check for installerready.exe or installerready.bat ---
    found_installer = False
    for root, dirs, files in os.walk(extract_path):
        for f in files:
            if f.lower() in ["installerready.exe", "installerready.bat"]:
                found_installer = True
                break

    if found_installer:
        print(f"✅ Installer file found in {repo} — ready to install.")
        return {"status": "ready", "path": extract_path}
    else:
        print(f"⚠️ No installer found in {repo}. Repo downloaded only.")
        return {"status": "no_installer", "path": extract_path}
