import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import subprocess
from downloader import download_github_repo

INSTALLERREADY_REPO = "https://github.com/coltonsr77/installerready"

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

        # Progress bar for download
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

        self.progress_label.configure(text="📦 Downloading repository...")
        self.progress_bar.set(0.1)
        thread = threading.Thread(target=self.download_repo_thread, args=(repo, path))
        thread.start()

    def download_repo_thread(self, repo, path):
        try:
            # Step 1: Download main repo
            result = download_github_repo(repo, path)
            self.progress_bar.set(0.6)

            if result["status"] == "ready":
                self.progress_label.configure(text="✅ Project downloaded successfully!")

                # Step 2: Download InstallerReady repo automatically
                self.progress_label.configure(text="⬇️ Downloading InstallerReady helper...")
                ir_path = os.path.join(path, "InstallerReady")
                ir_result = download_github_repo(INSTALLERREADY_REPO, ir_path)
                self.progress_bar.set(0.9)

                if ir_result["status"] == "ready":
                    self.progress_label.configure(text="✅ InstallerReady downloaded successfully!")
                else:
                    self.progress_label.configure(text="⚠️ InstallerReady repo downloaded (no installer detected).")

                # Step 3: Look for installerready.exe
                self.find_and_run_installer(result["path"])

            else:
                self.progress_label.configure(
                    text="⚠️ Oops! We can’t install this project, but we downloaded the repo."
                )
                self.progress_bar.set(1)
                # Still try to get InstallerReady
                ir_path = os.path.join(path, "InstallerReady")
                download_github_repo(INSTALLERREADY_REPO, ir_path)

        except Exception as e:
            self.progress_label.configure(text="❌ Installation failed.")
            self.progress_bar.set(0)
            messagebox.showerror("Error", str(e))

        finally:
            self.progress_bar.set(1)

    def find_and_run_installer(self, base_path):
        """Look for installerready.exe and optionally run it."""
        installer_file = None
        for root, dirs, files in os.walk(base_path):
            for f in files:
                if f.lower() == "installerready.exe":
                    installer_file = os.path.join(root, f)
                    break
            if installer_file:
                break

        if installer_file:
            self.ask_run_installer(installer_file)
        else:
            self.progress_label.configure(
                text="⚠️ Installer not found, but repository downloaded."
            )

    def ask_run_installer(self, installer_path):
        """Ask user to run installerready.exe."""
        answer = messagebox.askyesno(
            "Run Installer",
            f"Installer file found:\n\n{installer_path}\n\nDo you want to run it now?"
        )

        if answer:
            try:
                subprocess.Popen([installer_path], shell=True)
                self.progress_label.configure(text="🚀 Installer launched successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch installer:\n{e}")
        else:
            self.progress_label.configure(text="Installer ready, but not launched.")

    def show_about(self):
        messagebox.showinfo("About", "GitHub Installer v0.3\nCreated by coltonsr77")


if __name__ == "__main__":
    app = InstallerApp()
    app.mainloop()
