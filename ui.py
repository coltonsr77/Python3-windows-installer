import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
import webbrowser
from downloader import download_github_repo

class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Project Installer")
        self.geometry("500x450")
        self.resizable(False, False)

        self.repo_url = ctk.StringVar()
        self.install_path = ctk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # GitHub URL Entry
        ctk.CTkLabel(self, text="GitHub Repository URL:").pack(pady=10)
        ctk.CTkEntry(self, textvariable=self.repo_url, width=400).pack()

        # Folder selection
        ctk.CTkButton(self, text="Choose Install Folder", command=self.choose_folder).pack(pady=10)
        ctk.CTkLabel(self, textvariable=self.install_path, text_color="gray").pack()

        # Progress label
        self.progress_label = ctk.CTkLabel(self, text="")
        self.progress_label.pack(pady=10)

        # Install button
        ctk.CTkButton(self, text="Install", command=self.start_install).pack(pady=10)

        # New: InstallerReady Downloader button
        ctk.CTkButton(
            self,
            text="InstallerReady Downloader",
            command=self.open_installerready
        ).pack(pady=5)

        # About button
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

        self.progress_label.configure(text="📦 Downloading repository...")
        thread = threading.Thread(target=self.download_repo_thread, args=(repo, path))
        thread.start()

    def download_repo_thread(self, repo, path):
        try:
            result = download_github_repo(repo, path)

            if result["status"] == "ready":
                self.progress_label.configure(text="✅ Installer file found! Preparing to run...")
                install_path = result["path"]

                # Look for installerready.exe or .bat
                installer_file = None
                for root, dirs, files in os.walk(install_path):
                    for f in files:
                        if f.lower() in ["installerready.exe", "installerready.bat"]:
                            installer_file = os.path.join(root, f)
                            break
                    if installer_file:
                        break

                if installer_file:
                    self.ask_run_installer(installer_file)
                else:
                    self.progress_label.configure(
                        text="⚠️ Installer not found (unexpected). Repo downloaded."
                    )

            else:
                self.progress_label.configure(
                    text="⚠️ Oops! We can’t install this project, but we downloaded the repo."
                )

        except Exception as e:
            self.progress_label.configure(text="❌ Installation failed.")
            messagebox.showerror("Error", str(e))

    def ask_run_installer(self, installer_path):
        """Ask user to run the installerready file."""
        answer = messagebox.askyesno(
            "Run Installer",
            f"Installer file found:\n\n{installer_path}\n\nDo you want to run it now?"
        )

        if answer:
            try:
                if installer_path.lower().endswith(".exe"):
                    subprocess.Popen([installer_path], shell=True)
                elif installer_path.lower().endswith(".bat"):
                    subprocess.Popen(["cmd", "/c", installer_path], shell=True)
                self.progress_label.configure(text="🚀 Installer launched successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch installer:\n{e}")
        else:
            self.progress_label.configure(text="Installer ready, but not launched.")

    def open_installerready(self):
        """Open the InstallerReady GitHub page in the default browser."""
        url = "https://github.com/coltonsr77/installerready"
        webbrowser.open(url)

    def show_about(self):
        messagebox.showinfo("About", "GitHub Installer v0.1\nCreated by coltonsr77")
