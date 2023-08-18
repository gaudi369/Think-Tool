import tkinter as tk
from tkinter import Button, Label, Entry
import subprocess
import sys
import os

def launch_program(command, api_key):
    """
    Launches the given command in a subprocess.
    """
    os.environ['OPENAI_API_KEY'] = api_key  # Setting the API key as an environment variable
    print(f"Api key set: {api_key}")
    print(f"Executing command: {command}")
    subprocess.Popen(command, shell=True)

class ProgramLauncher(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window settings
        self.title('Program Launcher')  
        self.geometry('500x400')  # Set window size

        # Title label
        title_label = Label(self, text="Think Tool", font=('Arial', 24))
        title_label.pack(pady=20)  # Add padding above and below

        # API Key Entry
        self.api_key_label = Label(self, text="OpenAI API Key:")
        self.api_key_label.pack(pady=10)
        self.api_key_entry = Entry(self, width=60)
        self.api_key_entry.pack(pady=10)

        # Buttons for each program
        self.add_program_button("Program 1", f"{sys.executable} ./Study_Guide.py")
        self.add_program_button("Program 2", f"{sys.executable} ./babble_challenge.py")

    def add_program_button(self, label, command):
        """
        Adds a button to the launcher.
        """
        btn = Button(self, text=label, command=lambda: launch_program(command, self.api_key_entry.get()))
        btn.pack(fill=tk.X, padx=50, pady=5)

if __name__ == "__main__":
    app = ProgramLauncher()
    app.mainloop()
