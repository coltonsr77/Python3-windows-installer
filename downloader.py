import requests
import zipfile
import io
import os

def download_github_repo(repo_url, dest_folder):
    """
    Downloads a GitHub repository as a ZIP and extracts it.
    Supports URLs like: https://github.com/username/repo
    """
    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]

    # Convert to ZIP download URL
    zip_url = repo_url + "/archive/refs/heads/main.zip"

    response = requests.get(zip_url)
    if response.status_code != 200:
        raise Exception("Failed to download repository. Check URL or repo visibility.")

    zip_data = zipfile.ZipFile(io.BytesIO(response.content))

    extract_path = os.path.join(dest_folder, os.path.basename(repo_url))
    os.makedirs(extract_path, exist_ok=True)

    zip_data.extractall(extract_path)
    zip_data.close()

    return extract_path
