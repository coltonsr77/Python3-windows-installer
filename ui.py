import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from downloader import download_github_repo

class InstallerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GitHub Project Installer")
        self.geometry("500x400")

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

        self.progress_label.configure(text="Downloading...")
        thread = threading.Thread(target=self.download_repo_thread, args=(repo, path))
        thread.start()

    def download_repo_thread(self, repo, path):
        try:
            download_github_repo(repo, path)
            self.progress_label.configure(text="✅ Installation complete!")
        except Exception as e:
            self.progress_label.configure(text="❌ Installation failed.")
            messagebox.showerror("Error", str(e))

    def show_about(self):
        messagebox.showinfo("About", "GitHub Installer v1.0\nCreated by coltonsr77")
