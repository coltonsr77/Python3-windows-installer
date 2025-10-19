import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
import sys

# Ensure current folder is first in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from downloader import download_github_repo, download_latest_release

HELPER_REPO_URL = "https://github.com/coltonsr77/installerready"


class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Project Installer")
        self.geometry("600x400")
        self.resizable(False, False)

        self.repo_url = ctk.StringVar()
        self.output_dir = os.getcwd()

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="GitHub Project Installer", font=("Arial", 20, "bold")).pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.repo_url, placeholder_text="Enter GitHub repository URL...").pack(padx=20, pady=10, fill="x")
        ctk.CTkButton(self, text="Select Install Folder", command=self.select_output_folder).pack(pady=5)
        self.folder_label = ctk.CTkLabel(self, text=f"Install Path: {self.output_dir}")
        self.folder_label.pack()
        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)
        self.progress_label = ctk.CTkLabel(self, text="Ready.")
        self.progress_label.pack()
        ctk.CTkButton(self, text="Install Project", command=self.start_install).pack(pady=10)
        ctk.CTkButton(self, text="About", command=self.show_about).pack(pady=5)

    def select_output_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path
            self.folder_label.configure(text=f"Install Path: {self.output_dir}")

    def start_install(self):
        repo_url = self.repo_url.get().strip()
        if not repo_url:
            messagebox.showwarning("Missing URL", "Please enter a GitHub repository URL.")
            return
        threading.Thread(target=self.run_install, args=(repo_url,), daemon=True).start()

    def run_install(self, repo_url):
        self.update_progress(0, "Starting download...")
        try:
            # Step 1: Download user repo
            result = download_github_repo(repo_url, self.output_dir, self.update_progress)

            if result["status"] == "ready":
                self.update_progress(1.0, "InstallerReady found! Installation complete.")
                messagebox.showinfo("Success", "Project installed and ready.")
                return

            elif result["status"] == "no_installer":
                self.update_progress(0.9, "No installer found — downloading InstallerReady...")
                installer_result = download_latest_release(
                    HELPER_REPO_URL,
                    self.output_dir,
                    self.update_progress
                )

                if installer_result["status"] in ("ran", "no_exe"):
                    messagebox.showinfo(
                        "InstallerReady",
                        "InstallerReady downloaded and started."
                        if installer_result["status"] == "ran"
                        else "InstallerReady downloaded, but .exe not found."
                    )
                else:
                    messagebox.showwarning("InstallerReady", f"Failed to run InstallerReady: {installer_result.get('error', 'Unknown error')}")

            elif result["status"] == "error":
                self.update_progress(1.0, "Failed to download project.")
                messagebox.showerror("Error", f"Download failed: {result['error']}")

        except Exception as e:
            self.update_progress(1.0, "Error during installation.")
            messagebox.showerror("Installer Error", str(e))

    def update_progress(self, percent, message):
        self.progress.set(percent)
        self.progress_label.configure(text=message)
        self.update_idletasks()

    def show_about(self):
        messagebox.showinfo(
            "About",
            "GitHub Installer v0.3\nCreated by Coltonsr77\n\n"
            "This installer downloads a GitHub project and, if needed, automatically "
            "downloads and runs the latest release of InstallerReady."
        )


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
