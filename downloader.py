import requests
import zipfile
import io
import os
import re
import subprocess
import sys


def get_repo_name(repo_url: str) -> str:
    """Extract repository name from a GitHub URL."""
    match = re.search(r"github\.com/[^/]+/([^/]+)", repo_url)
    if match:
        return match.group(1).replace(".git", "")
    return "downloaded_repo"


def download_latest_release(repo_url: str, save_path: str, progress_callback=None):
    """
    Download the latest release ZIP file of a GitHub repo.
    Extract all files and run installerready.exe if found.
    """
    try:
        repo_name = get_repo_name(repo_url)
        match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
        if not match:
            raise ValueError("Invalid GitHub repository URL")

        owner, repo = match.groups()
        api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"

        if progress_callback:
            progress_callback(0.05, f"Fetching latest release for {repo_name}...")

        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        release_data = response.json()

        # Get ZIP asset or source ZIP URL
        zip_url = None
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".zip"):
                zip_url = asset["browser_download_url"]
                break

        # If no release ZIP, fallback to source code ZIP
        if not zip_url:
            zip_url = release_data.get("zipball_url")

        if not zip_url:
            raise RuntimeError("No release ZIP found.")

        if progress_callback:
            progress_callback(0.2, "Downloading InstallerReady release...")

        zip_response = requests.get(zip_url, stream=True)
        zip_response.raise_for_status()

        total = int(zip_response.headers.get("content-length", 0))
        downloaded = 0
        buffer = io.BytesIO()

        for chunk in zip_response.iter_content(chunk_size=8192):
            if chunk:
                buffer.write(chunk)
                downloaded += len(chunk)
                if total > 0 and progress_callback:
                    percent = 0.2 + (downloaded / total) * 0.6
                    progress_callback(percent, "Downloading release files...")

        buffer.seek(0)
        with zipfile.ZipFile(buffer) as zip_ref:
            zip_ref.extractall(save_path)

        if progress_callback:
            progress_callback(0.9, "Extracting all files...")

        exe_path = None
        for root, _, files in os.walk(save_path):
            for file in files:
                if file.lower() == "installerready.exe":
                    exe_path = os.path.join(root, file)
                    break
            if exe_path:
                break

        if progress_callback:
            progress_callback(1.0, "Download complete.")

        if exe_path:
            if progress_callback:
                progress_callback(1.0, "Running InstallerReady...")
            subprocess.Popen([exe_path], shell=True)
            return {"status": "ran", "path": exe_path}

        return {"status": "no_exe", "path": save_path}

    except Exception as e:
        if progress_callback:
            progress_callback(1.0, f"Failed: {e}")
        return {"status": "error", "error": str(e)}
