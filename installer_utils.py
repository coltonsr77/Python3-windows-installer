import subprocess
import os

def install_requirements(path):
    req_file = os.path.join(path, "requirements.txt")
    if os.path.exists(req_file):
        subprocess.run(["pip", "install", "-r", req_file])
