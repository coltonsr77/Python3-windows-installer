import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
from downloader import download_github_repo

HELPER_REPO = "https://github.com/coltonsr77/installerready"

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
            self.update_progress(0.05, "Starting download...")
            result = download_github_repo(repo, path, self.update_progress)

            if result["status"] == "ready":
                self.update_progress(0.9, f"✅ {result['repo_name']} ready, downloading helper...")
                helper_path = os.path.join(path, f"{result['repo_name']}_helper")
                download_github_repo(HELPER_REPO, helper_path, self.update_progress)
                self.find_and_run_installer(result["path"])
            elif result["status"] == "no_installer":
                self.update_progress(1.0, f"⚠️ No installerready.exe found, repo downloaded.")
                helper_path = os.path.join(path, f"{result['repo_name']}_helper")
                download_github_repo(HELPER_REPO, helper_path, self.update_progress)
            else:
                self.update_progress(1.0, "❌ Failed to download project.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.update_progress(1.0, "❌ Installation failed.")

    def find_and_run_installer(self, base_path):
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if f.lower() == "installerready.exe":
                    installer_path = os.path.join(root, f)
                    answer = messagebox.askyesno(
                        "Run Installer",
                        f"Installer found:\n{installer_path}\n\nRun it now?"
                    )
                    if answer:
                        subprocess.Popen([installer_path], shell=True)
                        self.update_progress(1.0, "🚀 Installer launched.")
                    return
        self.update_progress(1.0, "⚠️ No installerready.exe found in project.")

    def show_about(self):
        messagebox.showinfo("About", "GitHub Installer v0.3\nCreated by coltonsr77")


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
