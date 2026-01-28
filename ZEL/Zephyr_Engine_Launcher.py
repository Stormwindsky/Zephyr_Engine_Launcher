import tkinter as tk
from tkinter import messagebox
import subprocess
import os

# Project: Zephyr Engine Launcher
# Author: Stormwindsky
# License: MIT
# Platform: Linux (Optimized for Linux Mint/Ubuntu)

class ZephyrLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Zephyr Engine Launcher")
        self.root.geometry("400x280")
        self.root.resizable(False, False)
        
        # Background and Style
        self.root.configure(bg="#2c3e50")

        # Main Title
        self.label = tk.Label(root, text="ZEPHYR ENGINE", font=("Helvetica", 18, "bold"), 
                              bg="#2c3e50", fg="#ecf0f1")
        self.label.pack(pady=20)

        # Button for TwoD
        self.btn_twod = tk.Button(root, text="Launch TwoD", 
                                  width=20, height=2,
                                  command=self.run_twod, 
                                  bg="#27ae60", fg="white",
                                  font=("Helvetica", 10, "bold"))
        self.btn_twod.pack(pady=10)

        # Button for ThreeD (Disabled for now)
        self.btn_threed = tk.Button(root, text="Launch ThreeD", 
                                    width=20, height=2,
                                    command=self.run_threed,
                                    bg="#2980b9", fg="white",
                                    font=("Helvetica", 10, "bold"))
        self.btn_threed.pack(pady=10)

        # Footer
        self.footer = tk.Label(root, text="Created by Stormwindsky | MIT License", 
                               font=("Helvetica", 8), bg="#2c3e50", fg="#95a5a6")
        self.footer.pack(side="bottom", pady=15)

    def run_twod(self):
        # Path to twod_engine.py in the same directory
        script_path = os.path.join(os.path.dirname(__file__), "twod_engine.py")
        
        if os.path.exists(script_path):
            try:
                # Runs the python engine
                subprocess.Popen(["python3", script_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch TwoD: {e}")
        else:
            messagebox.showwarning("File Not Found", "Error: 'twod_engine.py' not found in this folder.")

    def run_threed(self):
        # Future-proof for ThreeD.nim
        messagebox.showinfo("ThreeD Engine", "ThreeD (3D Engine) is not yet implemented.\nStay tuned!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ZephyrLauncher(root)
    root.mainloop()