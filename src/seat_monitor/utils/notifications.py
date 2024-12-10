# src/seat_monitor/utils/notifications.py
import os
import subprocess


def notify_mac(title: str, message: str):
    """Send a Mac notification and play a sound"""
    # Play system alert sound
    os.system("afplay /System/Library/Sounds/Glass.aiff")

    # Send notification
    apple_script = f"""
    display notification "{message}" with title "{title}" sound name "Glass"
    """
    subprocess.run(["osascript", "-e", apple_script])
