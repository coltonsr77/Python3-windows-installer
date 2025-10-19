import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
import zipfile
import requests
import io
import re
import sys

# Ensure current folder is first in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

HELPER_REPO_URL = "https://github.com/coltonsr77/installerready"
VERSION = "0.3"  # Installer version

class GitHubInstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"GitHub Installer v{VERSION}")
        self.geometry("600x400")
        self.resizable(False, False)
        self.install_path = os.getcwd()
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="GitHub Project Installer", font=("Arial", 20, "bold")).pack(pady=10)

        # Repo URL input
        self.repo_entry = ctk.CTkEntry(self, placeholder_text="Enter GitHub repository URL...")
        self.repo_entry.pack(padx=20, pady=10, fill="x")

        # Folder selection
        ctk.CTkButton(self, text="Select Install Folder", command=self.select_folder).pack(pady=5)
        self.folder_label = ctk.CTkLabel(self, text=f"Install Path: {self.install_path}")
        self.folder_label.pack()

        # Progress bar
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)
        self.progress_label = ctk.CTkLabel(self, text="Ready")
        self.progress_label.pack()

        # Install button
        ctk.CTkButton(self, text="Install Project", command=self.start_install).pack(pady=10)

        # About button
        ctk.CTkButton(self, text="About", command=self.show_about).pack(pady=5)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.install_path = path
            self.folder_label.configure(text=f"Install Path: {self.install_path}")

    def update_progress(self, percent, message):
        self.progress.set(percent)
        self.progress_label.configure(text=message)
        self.update_idletasks()

    def start_install(self):
        repo_url = self.repo_entry.get().strip()
        if not repo_url:
            messagebox.showwarning("Missing URL", "Please enter a GitHub repository URL.")
            return
        threading.Thread(target=self.download_and_run, args=(repo_url,), daemon=True).start()

    def get_repo_name(self, repo_url):
        match = re.search(r"github\.com/[^/]+/([^/]+)", repo_url)
        if match:
            return match.group(1).replace(".git", "")
        return "downloaded_repo"

    def download_and_run(self, repo_url):
        self.update_progress(0.05, "Downloading repository...")
        try:
            repo_name = self.get_repo_name(repo_url)
            zip_url = f"{repo_url}/archive/refs/heads/main.zip"
            r = requests.get(zip_url, stream=True)
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            downloaded = 0
            buffer = io.BytesIO()
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        self.update_progress(min(0.8, downloaded / total * 0.8), "Downloading repository...")
            buffer.seek(0)

            # Extract ZIP
            with zipfile.ZipFile(buffer) as zip_ref:
                zip_ref.extractall(self.install_path)

            self.update_progress(0.9, "Checking for installer...")
            exe_path = None
            for root, _, files in os.walk(self.install_path):
                for file in files:
                    if file.lower() == "installerready.exe":
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break

            if exe_path:
                self.update_progress(1.0, "Running InstallerReady...")
                subprocess.Popen([exe_path], shell=True)
                messagebox.showinfo("Success", "InstallerReady launched successfully!")
            else:
                self.update_progress(0.92, "No installer found — downloading latest release...")
                self.download_latest_release(HELPER_REPO_URL)

        except Exception as e:
            self.update_progress(1.0, f"Failed: {e}")
            messagebox.showerror("Error", str(e))

    def download_latest_release(self, repo_url):
        try:
            match = re.search(r"github\.com/([^/]+)/([^/]+)", repo_url)
            if not match:
                raise ValueError("Invalid GitHub repository URL")
            owner, repo = match.groups()
            api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
            self.update_progress(0.95, "Fetching latest release info...")
            r = requests.get(api_url)
            r.raise_for_status()
            release = r.json()
            zip_url = release.get("zipball_url")
            if not zip_url:
                raise RuntimeError("No release ZIP found.")
            self.update_progress(0.96, "Downloading release...")
            zip_resp = requests.get(zip_url, stream=True)
            zip_resp.raise_for_status()
            total = int(zip_resp.headers.get("content-length", 0))
            downloaded = 0
            buffer = io.BytesIO()
            for chunk in zip_resp.iter_content(chunk_size=8192):
                if chunk:
                    buffer.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        self.update_progress(min(1.0, 0.96 + downloaded / total * 0.04), "Downloading release...")
            buffer.seek(0)
            with zipfile.ZipFile(buffer) as zip_ref:
                zip_ref.extractall(self.install_path)
            self.update_progress(1.0, "Release downloaded.")

            exe_path = None
            for root, _, files in os.walk(self.install_path):
                for file in files:
                    if file.lower() == "installerready.exe":
                        exe_path = os.path.join(root, file)
                        break
                if exe_path:
                    break

            if exe_path:
                subprocess.Popen([exe_path], shell=True)
                messagebox.showinfo("Success", "InstallerReady launched successfully!")
            else:
                messagebox.showwarning("Missing EXE", "InstallerReady downloaded but .exe not found.")

        except Exception as e:
            messagebox.showerror("Release Download Error", str(e))

    def show_about(self):
        messagebox.showinfo(
            "About GitHub Installer",
            f"GitHub Installer v{VERSION}\nCreated by Coltonsr77\n\n"
            "Downloads GitHub projects and automatically runs InstallerReady if needed."
        )


if __name__ == "__main__":
    app = GitHubInstallerApp()
    app.mainloop()
