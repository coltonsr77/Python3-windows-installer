import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
from downloader import download_github_repo, download_latest_release

HELPER_OWNER = "coltonsr77"
HELPER_REPO = "installerready"

class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Project Installer")
        self.geometry("500x470")
        self.resizable(False, False)

        self.repo_url = ctk.StringVar()
        self.install_path = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="GitHub Repository URL:").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.repo_url, width=400).pack()

        ctk.CTkButton(self, text="Choose Install Folder", command=self.choose_folder).pack(pady=10)
        ctk.CTkLabel(self, textvariable=self.install_path, text_color="gray").pack()

        self.progress_label = ctk.CTkLabel(self, text="")
        self.progress_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        ctk.CTkButton(self, text="Install", command=self.start_install).pack(pady=10)
        ctk.CTkButton(self, text="About", command=self.show_about).pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.install_path.set(folder)

    def start_install(self):
        repo = self.repo_url.get().strip()
        path = self.install_path.get().strip()

        if not repo or not path:
            messagebox.showerror("Error", "Please provide a GitHub URL and install folder.")
            return

        thread = threading.Thread(target=self.download_project_and_helper, args=(repo, path))
        thread.start()

    def update_progress(self, value, message):
        self.progress_bar.set(value)
        self.progress_label.configure(text=message)

    def download_project_and_helper(self, repo, path):
        try:
            self.update_progress(0.05, "Starting project download...")
            result = download_github_repo(repo, path, self.update_progress)

            if result["status"] in ("ready", "no_installer"):
                self.update_progress(0.9, "⬇️ Downloading latest InstallerReady release...")
                helper_file = download_latest_release(HELPER_OWNER, HELPER_REPO, path, self.update_progress)

                if helper_file and os.path.exists(helper_file):
                    self.update_progress(1.0, "🚀 Launching InstallerReady...")
                    subprocess.Popen([helper_file], shell=True)
                else:
                    self.update_progress(1.0, "⚠️ Could not download InstallerReady release.")
            else:
                self.update_progress(1.0, "❌ Project download failed.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_progress(1.0, "❌ Installation failed.")

    def show_about(self):
        messagebox.showinfo("About", "GitHub Installer v0.3\nCreated by coltonsr77")


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
