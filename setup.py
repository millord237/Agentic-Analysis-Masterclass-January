#!/usr/bin/env python
"""
Auto-setup script for Agentic Analysis Masterclass
Run this once after cloning to set up the environment and start the app.
"""
import subprocess
import sys
import os
import webbrowser
import time

def main():
    print("=" * 60)
    print("  AGENTIC ANALYSIS MASTERCLASS - AUTO SETUP")
    print("=" * 60)

    # Install requirements
    print("\n[1/3] Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
    print("      Dependencies installed!")

    # Ensure data folder exists
    print("\n[2/3] Setting up data folder...")
    os.makedirs("data", exist_ok=True)
    print("      Data folder ready!")

    # Start the app
    print("\n[3/3] Starting the app...")
    print("\n" + "=" * 60)
    print("  APP RUNNING AT: http://localhost:3000")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    # Open browser after a short delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:3000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    # Run the app
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
